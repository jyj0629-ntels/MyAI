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
        """Collect from several providers concurrently; failures are captured per-provider."""
        targets = [p for p in providers if p in SUPPORTED_PROVIDERS]
        if not targets:
            return []

        async def _guarded(provider: str) -> ScrapeResult:
            try:
                return await self.scrape(provider, prompt)
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

    async def scrape(self, provider: str, prompt: str) -> ScrapeResult:
        await asyncio.sleep(0)  # keep it awaitable / cooperative
        label = self._LABELS.get(provider, provider)
        text = (
            f"[{label} 웹 응답 - 임시 목업]\n"
            f"질문: {prompt}\n"
            f"이 텍스트는 실제 웹 스크래핑 대신 사용되는 목업 응답입니다. "
            f"Playwright 스크래퍼가 연결되면 이 자리에 {label}의 실제 웹 답변이 채워집니다."
        )
        return ScrapeResult(provider, text, "SUCCESS")


def get_scraper() -> PublicAIScraper:
    """Single place to switch the active scraper implementation.

    Return PlaywrightPublicAIScraper() here once browser automation is ready.
    """
    return MockPublicAIScraper()
