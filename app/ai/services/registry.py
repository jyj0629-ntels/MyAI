from app.ai.providers.base import AIProvider
from app.ai.services.provider_loader import ProviderLoader

_GLOBAL_ORCHESTRATOR = None


class AIProviderRegistry:

    def __init__(self):

        self.providers: dict[str, AIProvider] = {}

    def register(
        self,
        provider: AIProvider
    ):

        provider_name = (
            provider.name.strip().lower()
        )

        if provider_name in self.providers:

            print()
            print("# --------------------------------")
            print("# PROVIDER ALREADY REGISTERED")
            print("# --------------------------------")
            print(provider_name)
            print("# --------------------------------")
            print()

            return

        self.providers[
            provider_name
        ] = provider

        print()
        print("# --------------------------------")
        print("# PROVIDER REGISTERED")
        print("# --------------------------------")
        print(provider_name)
        print("# --------------------------------")
        print()

    def get(
        self,
        name: str
    ) -> AIProvider:

        provider_name = (
            name.strip().lower()
        )

        if provider_name not in self.providers:

            print()
            print("# --------------------------------")
            print("# PROVIDER NOT FOUND")
            print("# --------------------------------")
            print(provider_name)
            print("# --------------------------------")
            print("# AVAILABLE PROVIDERS")
            print("# --------------------------------")

            for item in sorted(
                self.providers.keys()
            ):
                print(item)

            print("# --------------------------------")
            print()

            raise ValueError(
                f"AI Provider not registered: {provider_name}"
            )

        return self.providers[
            provider_name
        ]

    def list(self):

        return sorted(
            self.providers.keys()
        )


def create_orchestrator():

    global _GLOBAL_ORCHESTRATOR

    if _GLOBAL_ORCHESTRATOR is not None:
        return _GLOBAL_ORCHESTRATOR

    from app.ai.services.orchestrator import AIOrchestrator

    registry = AIProviderRegistry()

    loaded_providers = (
        ProviderLoader()
        .load_all()
    )

    for provider in loaded_providers:

        registry.register(
            provider
        )

    print()
    print("# --------------------------------")
    print("# FINAL PROVIDER LIST")
    print("# --------------------------------")

    for provider_name in (
        registry.list()
    ):
        print(provider_name)

    print("# --------------------------------")
    print()

    _GLOBAL_ORCHESTRATOR = AIOrchestrator(
        registry=registry
    )

    return _GLOBAL_ORCHESTRATOR
