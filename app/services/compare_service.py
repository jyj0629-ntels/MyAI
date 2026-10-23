"""Pipeline for /demo_compare:

    scrape Public AIs -> persist raw responses -> Local LLM cross-check summary -> persist summary.

The Local LLM step reuses the existing OllamaProvider (settings.LOCAL_LLM_MODEL) with the
cross-check prompt from the PRD. Nothing here touches the existing /demo or /ai/chat flow.
"""

from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.core.config import settings

from app.repositories.compare_repository import CompareRepository
from app.services.compare_scraper_service import get_scraper


_PROVIDER_LABELS = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "gemini": "Gemini",
}

# 각 Public AI의 강점에 맞춰 같은 질문을 다르게 표현하기 위한 provider별 지침.
_PROVIDER_STYLE = {
    "chatgpt": (
        "[대상 AI: ChatGPT]\n"
        "ChatGPT는 단계적 추론과 정돈된 서술형 설명에 강합니다. "
        "질문의 맥락을 단계별로 풀어 설명하고, 핵심을 bullet로 구조화해 답하도록 요청하세요."
    ),
    "claude": (
        "[대상 AI: Claude]\n"
        "Claude는 긴 맥락 이해와 신중하고 균형 잡힌 분석, 안전한 서술에 강합니다. "
        "장단점을 균형 있게 비교하고 근거와 함께 신중하게 답하도록 요청하세요."
    ),
    "gemini": (
        "[대상 AI: Gemini]\n"
        "Gemini는 최신 정보 종합과 표/비교 형태의 구조화된 요약에 강합니다. "
        "핵심을 표나 비교 형식으로 간결하게 정리하도록 요청하세요."
    ),
}


class CompareService:
    def __init__(self, repository: CompareRepository):
        self.repository = repository
        self.scraper = get_scraper()

    @staticmethod
    def _build_provider_prompt(provider: str, user_prompt: str) -> str:
        """같은 사용자 질문을, 해당 Public AI의 강점에 맞게 변형한 전송 프롬프트."""
        style = _PROVIDER_STYLE.get(
            provider,
            "[대상 AI]\n해당 AI의 강점을 살려 정확하고 구조화된 답변을 요청하세요.",
        )
        return (
            f"{style}\n\n"
            f"[사용자 질문]\n{user_prompt}\n\n"
            f"[요청] 위 질문에 대해 이 AI의 강점을 최대한 활용해, "
            f"정확하고 사용자가 이해하기 쉬운 형식으로 답변해 주세요."
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

        # 1) Build a provider-tailored prompt per AI, then scrape concurrently.
        prompt_map = {p: self._build_provider_prompt(p, user_prompt) for p in providers}
        scrape_results = await self.scraper.scrape_many_with_prompts(prompt_map)

        collected = []
        for result in scrape_results:
            self.repository.add_source_response(
                history_id=history.id,
                ai_provider=result.provider,
                raw_response=result.text,
                status=result.status,
                sent_prompt=prompt_map.get(result.provider),
            )
            if result.status == "SUCCESS":
                collected.append(result.as_dict())

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
