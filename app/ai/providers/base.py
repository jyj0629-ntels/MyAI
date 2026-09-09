import asyncio
from abc import ABC, abstractmethod

from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse
from app.core.config import settings


class AIProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def ask(self, request: AIRequest) -> AIResponse:
        pass

    @staticmethod
    def is_transient_error(error: Exception) -> bool:
        text = str(error).upper()
        return any(
            marker in text
            for marker in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "RATE_LIMIT", "RATE LIMIT", "OVERLOADED")
        )

    @classmethod
    async def call_with_retry(cls, call, *, on_attempt_error=None):
        """Awaits `call()`, retrying only transient provider errors with exponential backoff."""
        max_attempts = settings.PROVIDER_MAX_RETRIES + 1
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                return await call()
            except Exception as e:
                last_error = e

                if on_attempt_error:
                    on_attempt_error(attempt, max_attempts, e)

                is_last_attempt = attempt >= max_attempts
                if cls.is_transient_error(e) and not is_last_attempt:
                    backoff_seconds = settings.PROVIDER_RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
                    await asyncio.sleep(backoff_seconds)
                    continue

                raise

        raise last_error
