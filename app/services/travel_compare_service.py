"""2-round travel comparison pipeline.

Round 1: personalized prompt (user preferences included) -> each Public AI (fan-out).
Merge  : Ollama synthesizes a Round 2 prompt from all round-1 answers.
Round 2: that prompt -> each Public AI (fan-out).
Final  : Ollama merges round-2 answers into the final guidance for the user.

Reuses existing building blocks:
- MemoryItemService/MemoryQueryService + ContextPackageService  (personal profile)
- LocalBrainLLMService.build_provider_prompt                    (personalized prompt)
- MultiProviderOrchestrator.ask_all                             (fan-out to Public AIs)
- OllamaProvider.ask                                            (local LLM merge)
Nothing here touches the existing /demo, /demo_compare, /demo_dpi flows.
"""

from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.services.registry import create_orchestrator
from app.ai.services.multi_provider_orchestrator import MultiProviderOrchestrator
from app.core.config import settings

from app.services.context_package_service import ContextPackageService
from app.services.local_brain_llm_service import LocalBrainLLMService
from app.services.memory_item_service import MemoryItemService
from app.services.memory_query_service import MemoryQueryService
from app.repositories.memory_item_repository import MemoryItemRepository

from app.repositories.travel_compare_repository import TravelCompareRepository


TRAVEL_RESPONSE_FORMAT = """
- 핵심 추천 (일정/장소)
- 이유와 개인 맞춤 근거
- 예상 비용/유의사항
- 다음에 확인할 점
"""


class TravelCompareService:
    def __init__(self, db):
        self.db = db
        self.repository = TravelCompareRepository(db)
        self.orchestrator = create_orchestrator()

    # ---------- personal profile ----------

    def _load_profile(self, user_id, question):
        """Return (user_profile, project_context) reusing the /ai/chat memory pipeline."""
        if not user_id:
            return "", []
        try:
            memory_service = MemoryItemService(MemoryItemRepository(self.db))
            memories = MemoryQueryService(memory_service).query(user_id=user_id, question=question)
            preferences = [m.content for m in memories if m.type == "PREFERENCE"]
            goals = [m.content for m in memories if m.type == "GOAL"]
            projects = list(dict.fromkeys(
                [m.content.strip() for m in memories if m.type == "PROJECT"]
            ))
            pkg = ContextPackageService().build(
                preferences=preferences, goals=goals, projects=projects
            )
            return pkg.get("user_profile") or "", pkg.get("project_context") or []
        except Exception as exc:
            print(f"[WARN] travel profile load failed: {exc}")
            return "", []

    # ---------- fan-out ----------

    async def _fan_out(self, question, user_profile, project_context, providers):
        """Build a personalized prompt and query all selected Public AIs."""
        prompt = LocalBrainLLMService().build_provider_prompt(
            question=question,
            user_profile=user_profile,
            project_context=project_context,
            provider_name=settings.PRIMARY_PROVIDER,
            task_type="여행 계획",
            response_format=TRAVEL_RESPONSE_FORMAT,
        )
        request = AIRequest(question=question, prompt=prompt)
        request.selected_providers = providers
        multi = await MultiProviderOrchestrator(self.orchestrator.registry).ask_all(request)
        return multi.get("responses", [])

    # ---------- local LLM merges ----------

    @staticmethod
    def _responses_block(responses):
        blocks = []
        for item in responses:
            provider = item.get("provider", "")
            text = (item.get("summary") or item.get("answer") or "").strip()
            blocks.append(f"[{provider} 응답]\n{text}")
        return "\n\n".join(blocks) if blocks else "(수집된 응답 없음)"

    async def _ollama(self, prompt):
        request = AIRequest(
            question=prompt,
            provider=settings.LOCAL_LLM_PROVIDER or "ollama",
            think=True,
            max_tokens=settings.OLLAMA_THINK_NUM_PREDICT,
        )
        resp = await OllamaProvider().ask(request)
        if getattr(resp, "success", False) and (resp.answer or "").strip():
            return resp.answer.strip()
        raise RuntimeError(getattr(resp, "error", None) or "Local LLM call failed")

    async def _build_round2_prompt(self, user_prompt, round1_responses):
        merge_prompt = f"""[역할]
너는 여러 AI의 여행 답변을 종합해, 다음 라운드에서 각 AI에게 다시 물어볼 "개선된 단일 질문"을 만드는 편집자다.

[원래 사용자 질문]
{user_prompt}

[1차 각 AI 응답]
{self._responses_block(round1_responses)}

[지시]
1. 위 답변들의 공통점과 서로 다른/모순되는 부분을 파악하라.
2. 차이가 큰 쟁점(일정, 비용, 장소 선택 등)을 좁히기 위해 각 AI가 더 구체적으로 답하도록 유도하는 질문을 작성하라.
3. 출력은 다음 라운드에서 그대로 사용할 "질문 한 단락"만. 설명·머리말 없이 질문 본문만 한국어로 작성하라."""
        return await self._ollama(merge_prompt)

    async def _build_final(self, user_prompt, round2_responses):
        final_prompt = f"""[역할]
너는 여러 AI의 2차 여행 답변을 교차 검증해 사용자에게 최종 안내를 작성하는 분석 전문가다.

[사용자 질문]
{user_prompt}

[2차 각 AI 응답]
{self._responses_block(round2_responses)}

[지시]
1. 공통적으로 추천되는 핵심 일정/장소를 확정해 제시하라.
2. AI 간 의견이 갈리는 부분은 장단점과 함께 명시하라.
3. 사용자 성향(가성비·후기·간결한 비교 등)을 반영한 최종 결론을 작성하라.
출력은 한국어로, 아래 형식을 따르라.
{TRAVEL_RESPONSE_FORMAT}"""
        return await self._ollama(final_prompt)

    # ---------- pipeline ----------

    async def run(self, user_id, user_prompt, providers, llm_model_used=None):
        model_label = llm_model_used or settings.LOCAL_LLM_MODEL
        history = self.repository.create_history(
            user_id=user_id,
            user_prompt=user_prompt,
            llm_model_used=model_label,
            status="PROCESSING",
        )

        user_profile, project_context = self._load_profile(user_id, user_prompt)

        # Round 1
        try:
            round1 = await self._fan_out(user_prompt, user_profile, project_context, providers)
        except Exception as exc:
            round1 = []
            print(f"[WARN] travel round1 fan-out failed: {exc}")

        for item in round1:
            self.repository.add_round_response(
                history_id=history.id, round_no=1,
                ai_provider=item.get("provider", ""),
                raw_response=item.get("answer") or "",
                summary=item.get("summary") or "",
                status="SUCCESS",
            )

        if not round1:
            self.repository.update_result(
                history_id=history.id,
                final_result="1차 Public AI 응답을 수집하지 못해 진행할 수 없습니다.",
                status="FAILED",
            )
            return self.get_detail(history.id)

        # Merge -> Round 2 prompt
        try:
            round2_prompt = await self._build_round2_prompt(user_prompt, round1)
            self.repository.set_round2_prompt(history.id, round2_prompt)
        except Exception as exc:
            self.repository.update_result(
                history_id=history.id,
                final_result=f"2차 질문 생성 중 오류: {exc}",
                status="FAILED",
            )
            return self.get_detail(history.id)

        # Round 2
        try:
            round2 = await self._fan_out(round2_prompt, user_profile, project_context, providers)
        except Exception as exc:
            round2 = []
            print(f"[WARN] travel round2 fan-out failed: {exc}")

        for item in round2:
            self.repository.add_round_response(
                history_id=history.id, round_no=2,
                ai_provider=item.get("provider", ""),
                raw_response=item.get("answer") or "",
                summary=item.get("summary") or "",
                status="SUCCESS",
            )

        if not round2:
            self.repository.update_result(
                history_id=history.id,
                final_result="2차 Public AI 응답을 수집하지 못했습니다.",
                status="FAILED",
            )
            return self.get_detail(history.id)

        # Final merge
        try:
            final_text = await self._build_final(user_prompt, round2)
            self.repository.update_result(
                history_id=history.id, final_result=final_text, status="COMPLETED"
            )
        except Exception as exc:
            self.repository.update_result(
                history_id=history.id,
                final_result=f"최종 취합 중 오류: {exc}",
                status="FAILED",
            )

        return self.get_detail(history.id)

    # ---------- read helpers ----------

    @staticmethod
    def _history_to_dict(h):
        return {
            "id": h.id,
            "user_prompt": h.user_prompt,
            "round2_prompt": h.round2_prompt,
            "final_result": h.final_result,
            "llm_model_used": h.llm_model_used,
            "status": h.status,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }

    @staticmethod
    def _round_to_dict(r):
        return {
            "id": r.id,
            "round_no": r.round_no,
            "ai_provider": r.ai_provider,
            "raw_response": r.raw_response,
            "summary": r.summary,
            "status": r.status,
        }

    def get_history_list(self, limit=30):
        return [self._history_to_dict(h) for h in self.repository.get_history_list(limit)]

    def get_detail(self, history_id):
        history = self.repository.get_history(history_id)
        if history is None:
            return None
        rounds = self.repository.get_round_responses(history_id)
        data = self._history_to_dict(history)
        data["round1"] = [self._round_to_dict(r) for r in rounds if r.round_no == 1]
        data["round2"] = [self._round_to_dict(r) for r in rounds if r.round_no == 2]
        return data
