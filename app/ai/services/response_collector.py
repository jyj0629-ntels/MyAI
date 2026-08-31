from collections import defaultdict


class ResponseCollector:

    def collect(
        self,
        responses
    ):

        result = []

        for response in responses:

            if not response.success:
                continue

            result.append(
                {
                    "provider": response.provider,
                    "model": response.model,
                    "answer": response.answer
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
