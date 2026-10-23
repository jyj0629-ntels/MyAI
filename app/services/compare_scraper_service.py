"""Web-automation scraper for Public AIs that have no usable API (ChatGPT, Claude, Gemini...).

Design note
-----------
The real implementation is meant to drive a headless browser (Playwright) with a
persistent ``user_data_dir`` so the logged-in session/cookies are reused, then type the
prompt into each site and scrape the answer. That part is environment-specific (login
sessions, bot-detection, per-site DOM selectors) and is intentionally isolated behind the
``PublicAIScraper`` interface so it can be swapped in without touching the pipeline.

For now the shipped implementation is ``MockPublicAIScraper`` which returns deterministic
placeholder text. Swap ``get_scraper()`` to return a ``PlaywrightPublicAIScraper`` once the
browser automation is wired up.
"""

import asyncio
from abc import ABC, abstractmethod


# Providers this feature knows how to (eventually) scrape from the web.
SUPPORTED_PROVIDERS = ("chatgpt", "claude", "gemini")


class ScrapeResult:
    def __init__(self, provider: str, text: str, status: str):
        self.provider = provider
        self.text = text
        self.status = status  # SUCCESS | TIMEOUT | ERROR

    def as_dict(self):
        return {"provider": self.provider, "text": self.text, "status": self.status}


class PublicAIScraper(ABC):
    """Interface. Implementations collect one Public AI's web answer for a prompt."""

    @abstractmethod
    async def scrape(self, provider: str, prompt: str) -> ScrapeResult:
        ...

    async def scrape_many(self, providers: list[str], prompt: str) -> list[ScrapeResult]:
        """Collect from several providers concurrently using the SAME prompt."""
        prompt_map = {p: prompt for p in providers}
        return await self.scrape_many_with_prompts(prompt_map)

    async def scrape_many_with_prompts(self, prompt_map: dict[str, str]) -> list[ScrapeResult]:
        """Collect concurrently, each provider receiving ITS OWN tailored prompt."""
        targets = [p for p in prompt_map if p in SUPPORTED_PROVIDERS]
        if not targets:
            return []

        async def _guarded(provider: str) -> ScrapeResult:
            try:
                return await self.scrape(provider, prompt_map[provider])
            except Exception as exc:  # never let one provider kill the batch
                return ScrapeResult(provider, f"[{provider} 수집 실패] {exc}", "ERROR")

        results = await asyncio.gather(*[_guarded(p) for p in targets])
        return list(results)


class MockPublicAIScraper(PublicAIScraper):
    """Placeholder scraper. Returns canned text so the full pipeline works end-to-end.

    Replace with PlaywrightPublicAIScraper for real web collection.
    """

    _LABELS = {
        "chatgpt": "ChatGPT",
        "claude": "Claude",
        "gemini": "Gemini",
    }

    # provider별로 "실제 응답처럼 보이는" 목업 답변(프롬프트를 되풀이하지 않음).
    _MOCK_ANSWER = {
        "chatgpt": (
            "| 항목 | 내용 |\n"
            "| --- | --- |\n"
            "| 핵심 결론 | 단계적으로 보면 A안이 가장 균형적입니다. |\n"
            "| 주요 근거 | 비용·일정·난이도를 종합할 때 리스크가 가장 낮음 |\n"
            "| 추천/선택지 | A안(우선), B안(대안) |\n"
            "| 장점 | 실행이 단순하고 예측 가능 |\n"
            "| 단점/주의 | 최대 성과는 다소 보수적 |\n\n"
            "총평: 안정적으로 진행하려면 A안이 무난합니다."
        ),
        "claude": (
            "| 항목 | 내용 |\n"
            "| --- | --- |\n"
            "| 핵심 결론 | 조건에 따라 B안이 더 나을 수 있습니다. |\n"
            "| 주요 근거 | 장기적 유연성과 확장성 측면에서 우위 |\n"
            "| 추천/선택지 | B안(상황에 따라), A안(안전책) |\n"
            "| 장점 | 변화에 유연하게 대응 가능 |\n"
            "| 단점/주의 | 초기 준비 비용이 더 큼 |\n\n"
            "총평: 장기 관점이면 B안, 단기면 A안을 권합니다."
        ),
        "gemini": (
            "| 항목 | 내용 |\n"
            "| --- | --- |\n"
            "| 핵심 결론 | 핵심 지표만 보면 A안과 B안이 근소한 차이입니다. |\n"
            "| 주요 근거 | 최신 데이터 기준 비용 대비 효과가 비슷 |\n"
            "| 추천/선택지 | A안/B안 혼합 전략 |\n"
            "| 장점 | 두 방식의 이점을 절충 |\n"
            "| 단점/주의 | 관리 포인트가 늘어남 |\n\n"
            "총평: 여건이 되면 혼합 전략이 가장 효과적입니다."
        ),
    }

    async def scrape(self, provider: str, prompt: str) -> ScrapeResult:
        await asyncio.sleep(0)  # keep it awaitable / cooperative
        label = self._LABELS.get(provider, provider)
        answer = self._MOCK_ANSWER.get(
            provider,
            "| 항목 | 내용 |\n| --- | --- |\n| 핵심 결론 | 목업 응답 |\n\n총평: 샘플 응답입니다.",
        )
        text = f"[{label} 응답 · 데모 목업]\n{answer}"
        return ScrapeResult(provider, text, "SUCCESS")


def get_scraper() -> PublicAIScraper:
    """Single place to switch the active scraper implementation.

    Return PlaywrightPublicAIScraper() here once browser automation is ready.
    """
    return MockPublicAIScraper()
