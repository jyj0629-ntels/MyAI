from app.ai.providers.base import AIProvider
from app.ai.providers.mock import MockProvider
from app.ai.providers.openai_provider import OpenAIProvider


class AIProviderRegistry:

    def __init__(self):

        self.providers: dict[str, AIProvider] = {}

    def register(
        self,
        provider: AIProvider
    ):

        self.providers[provider.name] = provider

    def get(
        self,
        name: str
    ) -> AIProvider:

        if name not in self.providers:

            raise ValueError(
                f"AI Provider not registered: {name}"
            )

        return self.providers[name]

    def list(self):

        return list(self.providers.keys())


def create_orchestrator():

    from app.ai.services.orchestrator import AIOrchestrator

    registry = AIProviderRegistry()

    registry.register(
        MockProvider()
    )

    registry.register(
        OpenAIProvider()
    )

    return AIOrchestrator(
        registry=registry
    )
