from abc import ABC, abstractmethod

from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse


class AIProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def ask(self, request: AIRequest) -> AIResponse:
        pass
