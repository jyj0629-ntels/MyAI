"""Pipeline for /demo_compare:

    scrape Public AIs -> persist raw responses -> Local LLM cross-check summary -> persist summary.

The Local LLM step reuses the existing OllamaProvider (settings.LOCAL_LLM_MODEL) with the
cross-check prompt from the PRD. Nothing here touches the existing /demo or /ai/chat flow.
"""

from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.services.registry import create_orchestrator
from app.ai.services.multi_provider_orchestrator import MultiProviderOrchestrator
from app.core.config import settings

from app.repositories.compare_repository import CompareRepository


_PROVIDER_LABELS = {
    "gemini": "Gemini",
    "groq": "Groq",
    "mistral": "Mistral",
    "openai": "OpenAI",
    "chatgpt": "ChatGPT",
    "claude": "Claude",
}

# 각 Public AI의 강점에 맞춰 같은 질문을 다르게 표현하기 위한 provider별 지침.
_PROVIDER_STYLE = {
    "gemini": (
        "[대상 AI: Gemini]\n"
        "Gemini는 최신 정보 종합과 표/비교 형태의 구조화된 요약에 강합니다. "
        "핵심을 표나 비교 형식으로 간결하게 정리하도록 요청하세요."
    ),
    "groq": (
        "[대상 AI: Groq]\n"
        "Groq는 빠르고 간결하며 실용적인 결론 도출에 강합니다. "
        "군더더기 없이 핵심 결론과 근거 위주로 답하도록 요청하세요."
    ),
    "mistral": (
        "[대상 AI: Mistral]\n"
        "Mistral은 논리적이고 균형 잡힌 분석에 강합니다. "
        "장단점을 근거와 함께 균형 있게 정리하도록 요청하세요."
    ),
}


class CompareService:
    def __init__(self, repository: CompareRepository):
        self.repository = repository
        self.orchestrator = create_orchestrator()

    # 모든 Public AI가 동일한 형식으로 답하도록 하는 공통 출력 포맷.
    # (내용/접근은 AI별 강점에 맞게 다르되, 결과 틀은 통일해야 비교가 쉽다)
    _COMMON_OUTPUT_FORMAT = (
        "[공통 출력 형식]\n"
        "다른 AI의 답변과 나란히 비교하기 쉽도록, 반드시 아래 Markdown 표 형식으로 핵심을 요약해 주세요.\n"
        "| 항목 | 내용 |\n"
        "| --- | --- |\n"
        "| 핵심 결론 | ... |\n"
        "| 주요 근거 | ... |\n"
        "| 추천/선택지 | ... |\n"
        "| 장점 | ... |\n"
        "| 단점/주의 | ... |\n"
        "표 아래에 2~3문장 이내의 짧은 총평만 덧붙이고, 그 외 장황한 설명은 생략하세요."
    )

    @staticmethod
    def _build_provider_prompt(provider: str, user_prompt: str) -> str:
        """같은 사용자 질문을, 해당 Public AI의 강점에 맞게 변형하되, 출력 형식은 공통 표로 통일."""
        style = _PROVIDER_STYLE.get(
            provider,
            "[대상 AI]\n해당 AI의 강점을 살려 정확하고 구조화된 답변을 요청하세요.",
        )
        return (
            f"{style}\n\n"
            f"[사용자 질문]\n{user_prompt}\n\n"
            f"[요청] 위 질문에 대해 이 AI의 강점을 최대한 활용해 답변하되, "
            f"여러 AI의 결과를 비교하기 쉽도록 아래 공통 출력 형식을 반드시 지켜 주세요.\n\n"
            f"{CompareService._COMMON_OUTPUT_FORMAT}"
        )

    @staticmethod
    def _build_cross_check_prompt(user_prompt: str, collected: list[dict]) -> str:
        blocks = []
        for item in collected:
            label = _PROVIDER_LABELS.get(item["provider"], item["provider"])
            blocks.append(f"[{label} 응답]\n{item['text']}")
        collected_responses = "\n\n".join(blocks) if blocks else "(수집된 응답 없음)"

        return f"""[역할]
당신은 다양한 AI의 답변을 교차 검증하고 종합하는 분석 전문가입니다.

[사용자 질문]
{user_prompt}

[각 AI별 응답]
{collected_responses}

[지시 사항]
1. 각 AI 답변의 공통 핵심 내용을 요약하세요.
2. AI 간 의견이 상충되거나 다른 부분을 비교 명시하세요.
3. 종합적인 최종 결론을 작성하세요.
출력은 한국어로 작성하세요."""

    async def _ask_providers(self, prompt_map: dict) -> dict:
        """각 Public AI에 그 AI 전용 프롬프트로 실제 API 호출. {provider: answer} 반환."""
        answer_map = {}
        for provider, prompt in prompt_map.items():
            try:
                request = AIRequest(question=prompt, prompt=prompt)
                request.selected_providers = [provider]
                multi = await MultiProviderOrchestrator(self.orchestrator.registry).ask_all(request)
                responses = multi.get("responses", [])
                # selected_providers로 1개만 호출되므로 첫 응답 사용.
                match = next(
                    (r for r in responses if str(r.get("provider", "")).lower() == provider),
                    responses[0] if responses else None,
                )
                if match:
                    answer_map[provider] = (match.get("answer") or match.get("summary") or "").strip()
            except Exception as exc:
                print(f"[WARN] compare ask provider {provider} failed: {exc}")
        return answer_map

    async def _summarize(self, user_prompt: str, collected: list[dict]) -> str:
        prompt = self._build_cross_check_prompt(user_prompt, collected)
        request = AIRequest(
            question=prompt,
            provider=settings.LOCAL_LLM_PROVIDER or "ollama",
            think=True,
            max_tokens=settings.OLLAMA_THINK_NUM_PREDICT,
        )
        response = await OllamaProvider().ask(request)
        if getattr(response, "success", False) and (response.answer or "").strip():
            return response.answer.strip()
        # Surface the reason instead of silently returning empty.
        raise RuntimeError(getattr(response, "error", None) or "Local LLM summary failed")

    async def run(self, user_id, user_prompt, providers, llm_model_used=None):
        """Execute the full compare pipeline and return the persisted history + sources."""
        model_label = llm_model_used or settings.LOCAL_LLM_MODEL

        history = self.repository.create_history(
            user_id=user_id,
            user_prompt=user_prompt,
            llm_model_used=model_label,
            status="PROCESSING",
        )

        # 1) Build a provider-tailored prompt per AI, then call each real Public AI (API).
        prompt_map = {p: self._build_provider_prompt(p, user_prompt) for p in providers}
        answer_map = await self._ask_providers(prompt_map)

        collected = []
        for provider in providers:
            answer = answer_map.get(provider)
            status = "SUCCESS" if answer else "ERROR"
            raw = answer or "(응답을 받지 못했습니다)"
            self.repository.add_source_response(
                history_id=history.id,
                ai_provider=provider,
                raw_response=raw,
                status=status,
                sent_prompt=prompt_map.get(provider),
            )
            if answer:
                collected.append({"provider": provider, "text": answer, "status": "SUCCESS"})

        # 2) Local LLM cross-check summary.
        if not collected:
            self.repository.update_history_result(
                history_id=history.id,
                summary_result="수집된 Public AI 응답이 없어 요약을 생성할 수 없습니다.",
                status="FAILED",
            )
            return self.get_detail(history.id)

        try:
            summary = await self._summarize(user_prompt, collected)
            self.repository.update_history_result(
                history_id=history.id,
                summary_result=summary,
                status="COMPLETED",
            )
        except Exception as exc:
            self.repository.update_history_result(
                history_id=history.id,
                summary_result=f"요약 생성 중 오류가 발생했습니다: {exc}",
                status="FAILED",
            )

        return self.get_detail(history.id)

    # ---- read helpers ----

    @staticmethod
    def _history_to_dict(history):
        return {
            "id": history.id,
            "user_prompt": history.user_prompt,
            "summary_result": history.summary_result,
            "llm_model_used": history.llm_model_used,
            "status": history.status,
            "created_at": history.created_at.isoformat() if history.created_at else None,
        }

    @staticmethod
    def _source_to_dict(source):
        return {
            "id": source.id,
            "ai_provider": source.ai_provider,
            "sent_prompt": getattr(source, "sent_prompt", None),
            "raw_response": source.raw_response,
            "status": source.status,
            "created_at": source.created_at.isoformat() if source.created_at else None,
        }

    def get_history_list(self, limit=30):
        return [self._history_to_dict(h) for h in self.repository.get_history_list(limit)]

    def get_detail(self, history_id):
        history = self.repository.get_history(history_id)
        if history is None:
            return None
        sources = self.repository.get_source_responses(history_id)
        data = self._history_to_dict(history)
        data["source_responses"] = [self._source_to_dict(s) for s in sources]
        return data
