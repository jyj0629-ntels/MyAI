class MemoryConsolidationService:

    def consolidate(
        self,
        memories
    ):

        consolidated = {}

        for memory in memories:

            if memory.key not in consolidated:

                consolidated[
                    memory.key
                ] = memory

                continue

            existing = (
                consolidated[
                    memory.key
                ]
            )

            if (
                memory.confidence
                > existing.confidence
            ):
                consolidated[
                    memory.key
                ] = memory

        return list(
            consolidated.values()
        )
