class RelevantMemoryService:

    def filter(
        self,
        question: str,
        memories
    ):

        results = []

        question_lower = (
            question.lower()
        )

        for memory in memories:

            content = (
                memory.content.lower()
            )

            if (
                "myai" in question_lower
                and "myai" in content
            ):
                results.append(
                    memory
                )

                continue

            if (
                "redis" in question_lower
                and "redis" in content
            ):
                results.append(
                    memory
                )

                continue

        return results
