import asyncio
from abc import ABC, abstractmethod

from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse
from app.core.config import settings


class AIProvider(ABC):
    """
    Base class for every AI provider.

    Subclasses only implement `_ask_once()` (a single call attempt that returns an
    AIResponse, success or failure). `ask()` itself is NOT overridden by subclasses:
    it is a template method defined here that wraps `_ask_once()` with transient-error
    retry + exponential backoff. This makes retry behavior automatic for any provider,
    including ones added in the future, with zero retry-specific code in the subclass.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def _ask_once(self, request: AIRequest) -> AIResponse:
        pass

    @staticmethod
    def is_transient_error(text) -> bool:
        upper_text = str(text or "").upper()
        return any(
            marker in upper_text
            for marker in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "RATE_LIMIT", "RATE LIMIT", "OVERLOADED")
        )

    async def ask(self, request: AIRequest) -> AIResponse:
        max_attempts = settings.PROVIDER_MAX_RETRIES + 1
        response = None

        for attempt in range(1, max_attempts + 1):
            response = await self._ask_once(request)

            if getattr(response, "success", False):
                return response

            is_last_attempt = attempt >= max_attempts
            error_text = getattr(response, "error", None) or getattr(response, "answer", "")

            if is_last_attempt or not self.is_transient_error(error_text):
                return response

            backoff_seconds = settings.PROVIDER_RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
            print(
                f"[{self.name.upper()} RETRY] attempt={attempt}/{max_attempts} "
                f"transient error, retrying in {backoff_seconds:.1f}s"
            )
            await asyncio.sleep(backoff_seconds)

        return response

