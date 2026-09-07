from collections import defaultdict
from app.ai.services.response_summary_service import ResponseSummaryService


class ResponseCollector:

    def collect(
        self,
        responses
    ):

        result = []

        for response in responses:

            if not response.success:
                continue

            summary = (
                ResponseSummaryService()
                .summarize(
                    response.answer
                )
            )

            response_time_ms = getattr(response, "response_time_ms", None)
            if response_time_ms is None:
                perf = getattr(response, "performance", None) or {}
                response_time_ms = perf.get("response_time_ms")

            result.append(
                {
                    "provider": response.provider,
                    "model": response.model,
                    "answer": response.answer,
                    "summary": summary,
                    "response_time_ms": response_time_ms,
                }
            )

        return result

    def group_by_answer(
        self,
        responses
    ):

        groups = defaultdict(list)

        for item in responses:

            answer = (
                item["answer"]
                .strip()
            )

            groups[
                answer
            ].append(
                item["provider"]
            )

        return groups
