from app.core.config import settings

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

        fallback_order = []

        if provider_name:
            fallback_order.append(
                provider_name
            )

        fallback_providers = [
            provider.strip()
            for provider in (
                settings.FALLBACK_PROVIDERS
                or ""
            ).split(",")
            if provider.strip()
        ]

        for provider in (
            fallback_providers
        ):

            if provider not in fallback_order:

                fallback_order.append(
                    provider
                )

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

                print(e)

        if last_response:

            return last_response

        return AIResponse(
            provider="none",
            model="none",
            answer="No available AI provider.",
            success=False
        )
