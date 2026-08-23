from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse
from app.ai.providers.base import AIProvider


class AIOrchestrator:

    def __init__(self, registry):

        self.registry = registry

    async def ask(
        self,
        provider_name: str,
        request: AIRequest
    ) -> AIResponse:

        provider: AIProvider = self.registry.get(
            provider_name
        )

        return await provider.ask(
            request
        )
