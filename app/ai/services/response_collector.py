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

            result.append(
                {
                    "provider": response.provider,
                    "model": response.model,
                    "answer": response.answer,
                    "summary": summary
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
