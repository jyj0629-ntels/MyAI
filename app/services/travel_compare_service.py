"""2-round travel planning pipeline (STEP1 관광지 뽑기 -> STEP2 일정 계획).

STEP1: 구조화된 여행 폼으로 "관광지 TOP20" 프롬프트를 만들어 각 Public AI에 질의.
MERGE: Ollama가 STEP1 응답들을 종합해 여행지 구분([필수]/[경유]/[특별]) 표 + STEP2 일정 프롬프트를 자동 생성.
STEP2: 그 프롬프트로 각 Public AI에 재질의.
FINAL: Ollama가 STEP2 응답들을 교차검증해 최종 여행 계획(텍스트 표)을 생성.

데모 기준: 여행지 구분은 자동 분류, 산출물은 텍스트 표까지만(실제 .xlsx/지도 핀 생성 안 함).
개인 성향(DB 메모리)도 프롬프트에 함께 반영.
"""

from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.services.registry import create_orchestrator
from app.ai.services.multi_provider_orchestrator import MultiProviderOrchestrator
from app.core.config import settings

from app.services.context_package_service import ContextPackageService
from app.services.memory_item_service import MemoryItemService
from app.services.memory_query_service import MemoryQueryService
from app.repositories.memory_item_repository import MemoryItemRepository

from app.repositories.travel_compare_repository import TravelCompareRepository


class TravelCompareService:
    def __init__(self, db):
        self.db = db
        self.repository = TravelCompareRepository(db)
        self.orchestrator = create_orchestrator()

    # ---------- personal profile ----------

    def _load_profile(self, user_id, question):
        if not user_id:
            return ""
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
            return pkg.get("user_profile") or ""
        except Exception as exc:
            print(f"[WARN] travel profile load failed: {exc}")
            return ""

    # ---------- STEP1 prompt (관광지 TOP20) ----------

    @staticmethod
    def _step1_prompt(form, user_profile):
        country = form.get("country", "")
        region = form.get("region", "")
        period = form.get("period", "")
        must_see = form.get("must_see", "")
        profile_block = user_profile or "없음"
        return f"""[역할]
당신은 여행 전문가이며, '{country}'의 '{region}' 지역 전문 여행 가이드로서 현지 음식점, 숙소, 관광장소의 현재 기준 실시간 정보를 잘 알고 있습니다.

[여행정보]
여행국가 및 지역 : {country}의 {region}
여행기간 : {period}
여행 필수 관광지 or 지역 : {must_see}

[사용자 성향 및 선호]
{profile_block}

[특이사항]
- 결과 요청 내용만 간단히 표로 정리하고 긴 설명은 하지 말 것.
- 현지인이 주말마다 가는 흔한 곳은 배제하고, 일생에 한 번 가볼 만한 특별한 곳 위주로 추천.
- 반드시 해당 국가 관광청 사이트나 유명 관광 사이트에 많이 소개된 곳 기준으로 취합.

[결과 요청 내용]
1) 관광지 TOP20 리스트를 만들고, 많은 사람이 선호하는 우선순위로 정렬하되 같은 지역끼리 묶어 정렬.
2) 반드시 필수 관광지 '{must_see}' 를 리스트에 포함.
3) 다음 컬럼의 표로 정리: 지역 | 관광지명 | 관광지 설명/사이트 링크 | 추천 사유 | 추천월 | 주요특징 및 활동 | 비용(바트) | 비용(한화)
   - 추천월이 여행기간과 맞지 않는 곳은 표 맨 아래에 배치.
   - 각 관광지의 대략적 위경도(위도,경도)도 함께 표기(구글 지도 마킹용)."""

    # ---------- STEP2 prompt (Ollama가 STEP1 취합해 생성) ----------

    def _step2_prompt(self, form, user_profile, step1_responses):
        country = form.get("country", "")
        region = form.get("region", "")
        period = form.get("period", "")
        must_see = form.get("must_see", "")
        period_notes = form.get("period_notes", "")
        remarks = form.get("remarks", "")
        profile_block = user_profile or "없음"
        step1_block = self._responses_block(step1_responses)

        # Ollama에게: STEP1 응답을 종합해 여행지 구분표를 자동으로 만들고, 아래 일정 프롬프트를 완성하라.
        return f"""[역할]
너는 여행 일정 편집 전문가다. 아래 1차 관광지 조사 결과를 종합해, 각 Public AI에게 보낼 "여행 일정 계획 프롬프트"를 완성하라.

[여행정보]
여행국가/지역 : {country}의 {region}
여행기간 : {period}
필수 관광지 : {must_see}

[여행기간 특이사항]
{period_notes or '없음'}

[비고사항]
{remarks or '없음'}

[사용자 성향]
{profile_block}

[1차 관광지 조사 결과(각 AI)]
{step1_block}

[네가 할 일]
1. 위 결과를 종합해 관광지 목록을 만들고, 각 관광지를 [필수]/[경유]/[특별] 중 하나로 자동 분류한 "여행지 구분 표"를 작성하라(필수 관광지 '{must_see}'는 반드시 [필수]).
2. 그 표를 포함해, 아래 "여행 일정 Plan 요청사항"을 담은 완성된 프롬프트를 출력하라. 이 출력은 다음 라운드에서 각 Public AI에게 그대로 전달된다. 설명·머리말 없이 프롬프트 본문만 한국어로 출력하라.

[여행 일정 Plan 요청사항 - 반드시 포함]
- [필수] 기준으로 하루 일정을 잡되 이동·관광·식사(점심/저녁 각 1시간) 포함 최대 12시간.
- 가는/오는 길에 [경유] 관광지가 있으면 동선에 추가. 야시장/야경/저녁 포함 시 21시 이전 종료, 숙소 22시 이전 복귀.
- 도착일은 비행 피로로 숙소 근처 [경유]만 가볍게. 둘째날부터 날씨/우기·건기 최상 조건 우선, 힘든 일정을 앞쪽에 배치.
- 숙소는 이동시간 최소화로 고정하되 왕복 4시간 이상이면 해당 관광지 인근 숙소.
- 현재 환율로 비용 산출.
- 일정표 컬럼: 날짜 | 지역 | 관광지명 | 주요특징 및 활동 | 추천 사유 | 추천월 | 이동시간 | 이동거리(Km) | 비용(바트) | 비용(한화) | 사이트 링크 | 식사
- 이동거리(Km)와 대략 기름값 표기, 날짜별 비용 소계 및 총액(바트/한화).
- 각 관광지 위경도(위도,경도)를 날짜와 함께 표기(날짜별 구글 지도 마킹용, 색상은 날짜별 구분).
- 산출물은 텍스트 표로만 정리(엑셀/지도 파일 생성은 불필요)."""

    # ---------- fan-out ----------

    async def _fan_out(self, prompt, providers):
        request = AIRequest(question=prompt, prompt=prompt)
        request.selected_providers = providers
        multi = await MultiProviderOrchestrator(self.orchestrator.registry).ask_all(request)
        return multi.get("responses", [])

    # ---------- local LLM ----------

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

    async def _final(self, form, step2_responses):
        block = self._responses_block(step2_responses)
        prompt = f"""[역할]
너는 여러 AI의 여행 일정 답변을 교차 검증해 사용자에게 최종 여행 계획을 작성하는 분석 전문가다.

[여행정보]
{form.get('country','')}의 {form.get('region','')} / {form.get('period','')}

[2차 각 AI 일정 답변]
{block}

[지시]
1. 공통적으로 합리적인 날짜별 일정을 확정해 제시하라.
2. AI 간 갈리는 부분(동선·숙소·비용)은 장단점과 함께 명시하라.
3. 최종 일정표를 텍스트 표로 작성: 날짜 | 지역 | 관광지명 | 주요특징/활동 | 이동시간 | 이동거리(Km) | 비용(바트) | 비용(한화) | 식사.
4. 날짜별 비용 소계와 전체 총액(바트/한화), 그리고 관광지 위경도 목록(날짜별)을 덧붙여라.
출력은 한국어 텍스트로만 작성."""
        return await self._ollama(prompt)

    # ---------- pipeline ----------

    async def run(self, user_id, form, providers, llm_model_used=None):
        model_label = llm_model_used or settings.LOCAL_LLM_MODEL
        summary_question = f"{form.get('country','')} {form.get('region','')} 여행 {form.get('period','')}"

        history = self.repository.create_history(
            user_id=user_id,
            user_prompt=summary_question,
            llm_model_used=model_label,
            status="PROCESSING",
        )

        user_profile = self._load_profile(user_id, summary_question)

        # STEP1: 관광지 TOP20
        try:
            step1_prompt = self._step1_prompt(form, user_profile)
            step1 = await self._fan_out(step1_prompt, providers)
        except Exception as exc:
            step1 = []
            print(f"[WARN] travel step1 failed: {exc}")

        for item in step1:
            self.repository.add_round_response(
                history_id=history.id, round_no=1,
                ai_provider=item.get("provider", ""),
                raw_response=item.get("answer") or "",
                summary=item.get("summary") or "",
                status="SUCCESS",
            )

        if not step1:
            self.repository.update_result(
                history_id=history.id,
                final_result="1차 관광지 조사 응답을 수집하지 못했습니다.",
                status="FAILED",
            )
            return self.get_detail(history.id)

        # MERGE -> STEP2 프롬프트 (Ollama 자동 생성)
        try:
            step2_prompt = await self._ollama(self._step2_prompt(form, user_profile, step1))
            self.repository.set_round2_prompt(history.id, step2_prompt)
        except Exception as exc:
            self.repository.update_result(
                history_id=history.id,
                final_result=f"2차 일정 프롬프트 생성 중 오류: {exc}",
                status="FAILED",
            )
            return self.get_detail(history.id)

        # STEP2: 일정 계획
        try:
            step2 = await self._fan_out(step2_prompt, providers)
        except Exception as exc:
            step2 = []
            print(f"[WARN] travel step2 failed: {exc}")

        for item in step2:
            self.repository.add_round_response(
                history_id=history.id, round_no=2,
                ai_provider=item.get("provider", ""),
                raw_response=item.get("answer") or "",
                summary=item.get("summary") or "",
                status="SUCCESS",
            )

        if not step2:
            self.repository.update_result(
                history_id=history.id,
                final_result="2차 일정 응답을 수집하지 못했습니다.",
                status="FAILED",
            )
            return self.get_detail(history.id)

        # FINAL
        try:
            final_text = await self._final(form, step2)
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
