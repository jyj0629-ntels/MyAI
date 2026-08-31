from app.ai.providers.base import AIProvider

from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.groq_provider import GroqProvider

from app.ai.services.provider_loader import ProviderLoader

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

    for provider in (
        ProviderLoader()
        .load_all()
    ):

        registry.register(
            provider
        )

        print(
            f"[PROVIDER REGISTERED] "
            f"{provider.name}"
        )

    return AIOrchestrator(
        registry=registry
    )
