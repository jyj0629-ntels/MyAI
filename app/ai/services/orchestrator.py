from app.core.config import settings
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse


class AIOrchestrator:

    def __init__(self, registry):

        self.registry = registry

    async def ask(
        self,
        provider_name: str,
        request: AIRequest
    ) -> AIResponse:

        if provider_name:
            normalized_name = provider_name.strip().lower()
        else:
            normalized_name = ""

        if normalized_name in {"ollama", settings.LOCAL_LLM_PROVIDER.lower()}:
            from app.ai.providers.ollama_provider import OllamaProvider
            return await OllamaProvider().ask(request)

        available_providers = (
            self.registry.list()
        )

        fallback_order = []

        if provider_name:

            provider_name = (
                provider_name
                .strip()
                .lower()
            )

            if (
                provider_name
                in available_providers
            ):
                fallback_order.append(
                    provider_name
                )

        fallback_providers = [
            provider.strip().lower()
            for provider in (
                settings.FALLBACK_PROVIDERS
                or ""
            ).split(",")
            if provider.strip()
        ]

        for provider in fallback_providers:

            if provider not in available_providers:

                print()
                print("# --------------------------------")
                print("# UNKNOWN FALLBACK PROVIDER")
                print("# --------------------------------")
                print(provider)
                print("# --------------------------------")
                print()

                continue

            if provider not in fallback_order:

                fallback_order.append(
                    provider
                )

        print()
        print("# --------------------------------")
        print("# AVAILABLE PROVIDERS")
        print("# --------------------------------")
        print(available_providers)
        print("# --------------------------------")
        print()

        print()
        print("# --------------------------------")
        print("# PROVIDER FAILOVER ORDER")
        print("# --------------------------------")
        print(fallback_order)
        print("# --------------------------------")
        print()

        last_response = None

        for current_provider in fallback_order:

            try:

                print(
                    f"[TRY PROVIDER] "
                    f"{current_provider}"
                )

                provider = (
                    self.registry.get(
                        current_provider
                    )
                )

                response = await (
                    provider.ask(
                        request
                    )
                )

                if response.success:

                    print(
                        f"[PROVIDER SUCCESS] "
                        f"{current_provider}"
                    )

                    return response

                print(
                    f"[PROVIDER FAILED] "
                    f"{current_provider}"
                )

                last_response = response

            except Exception as e:

                print(
                    f"[FAILOVER] "
                    f"{current_provider}"
                )

                print(
                    str(e)
                )

        if last_response:

            return last_response

        return AIResponse(
            provider="none",
            model="none",
            answer="No available AI provider.",
            success=False
        )
