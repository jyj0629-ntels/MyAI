import asyncio

from app.core.config import settings

from app.ai.models.request import AIRequest

from app.ai.services.response_collector import ResponseCollector
from app.ai.services.consensus_engine import ConsensusEngine
from app.ai.services.local_consensus_service import LocalConsensusService
from app.ai.services.response_summary_service import ResponseSummaryService

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

            if provider_name == "ollama": 
                continue

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

                print()
                print("# --------------------------------")
                print("# PROVIDER EXCEPTION")
                print("# --------------------------------")
                print(str(result))
                print("# --------------------------------")
                print()

                continue

            if not getattr(
                result,
                "success",
                True
            ):
                print()
                print("# --------------------------------")
                print("# PROVIDER FAILED")
                print("# --------------------------------")
                print(result.provider)
                print(result.error)
                print("# --------------------------------")
                print()

                continue

            responses.append(
                result
            )

        print()
        print("# --------------------------------")
        print("# PROVIDER RESPONSES")
        print("# --------------------------------")

        for response in responses:

            print()
            print(
                f"[{response.provider}]"
            )

            print(
                response.answer[:300]
            )

            print("# --------------------------------")
            print()

        collector = (
            ResponseCollector()
        )

        collected = (
            collector.collect(
                responses
            )
        )

        summary_service = (
            ResponseSummaryService()
        )

        for item in collected:

            item["answer"] = (
                summary_service.summarize(
                    item["answer"]
            )
        )

        consensus = []

        selected = (
            {
                "mode": "multi",
                "response_count": len(collected)
            }
            if len(collected) >= 2
            else None
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
        print("Handled by Local LLM Judge")
        print("# --------------------------------")
        print()

        judge_request = ( 
            LocalConsensusService() 
            .build_request(
                request.question,
                collected
            )
        )

        return {
            "responses": collected,
            "consensus": consensus,
            "selected": selected,
            "judge_request": judge_request
        }
