import asyncio

from app.ai.models.request import AIRequest
from app.ai.services.response_collector import \
    ResponseCollector

from app.ai.services.consensus_engine import \
    ConsensusEngine


class MultiProviderOrchestrator:

    def __init__(
        self,
        registry
    ):
        self.registry = registry

    async def ask_all(
        self,
        request: AIRequest
    ):

        providers = (
            self.registry.list()
        )

        tasks = []

        for provider_name in providers:

            provider = (
                self.registry.get(
                    provider_name
                )
            )

            print(
                f"[PARALLEL START] "
                f"{provider_name}"
            )

            tasks.append(
                provider.ask(
                    request
                )
            )

        results = await (
            asyncio.gather(
                *tasks,
                return_exceptions=True
            )
        )

        responses = []

        for result in results:

            if isinstance(
                result,
                Exception
            ):
                continue

            responses.append(
                result
            )

        collector = (
            ResponseCollector()
        )

        collected = (
            collector.collect(
                responses
            )
        )

        grouped = (
            collector.group_by_answer(
                collected
            )
        )

        consensus = (
            ConsensusEngine()
            .calculate(
                grouped
            )
        )

        selected = (
            ConsensusEngine()
            .select(
                consensus
            )
        )

        required_responses = 2

        if len(collected) == 0:

            print()
            print("# --------------------------------")
            print("# NO PROVIDER RESPONSE")
            print("# --------------------------------")
            print("# --------------------------------")
            print()

            selected = None

        elif len(collected) == 1:

            print()
            print("# --------------------------------")
            print("# SINGLE PROVIDER MODE")
            print("# --------------------------------")
            print(
                collected[0]["provider"]
            )
            print("# --------------------------------")
            print()

            if settings.ALLOW_SINGLE_PROVIDER:

                selected = {
                    "mode": "single",
                    "response": collected[0]
                }

            else:

                selected = None

        else:

            selected = (
                ConsensusEngine()
                .select(
                    consensus
                )
            )

        provider_count = len(
            collected
        )
        
        print()
        print("# --------------------------------")
        print("# PROVIDER SUMMARY")
        print("# --------------------------------")
        print(
            f"consensus_threshold="
            f"{settings.CONSENSUS_THRESHOLD}"
        )
        print(
            f"selected="
            f"{selected}"
        )
        print("# --------------------------------")
        print()


        print()
        print("# --------------------------------")
        print("# CONSENSUS RESULT")
        print("# --------------------------------")
        print(consensus)
        print("# --------------------------------")
        print()

        return {
            "responses": collected,
            "consensus": consensus,
            "selected": selected
        }
