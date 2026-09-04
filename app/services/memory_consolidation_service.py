class MemoryConsolidationService:

    def consolidate(
        self,
        memories
    ):

        consolidated = {}

        for memory in memories:

            if not memory:
                continue

            key = (
                memory.key
                .strip()
                .lower()
            )

            if not key:
                continue

            if key not in consolidated:

                consolidated[key] = memory

                continue

            existing = (
                consolidated[key]
            )

            existing_score = (
                float(existing.confidence)
                * float(existing.importance)
            )

            current_score = (
                float(memory.confidence)
                * float(memory.importance)
            )

            if current_score > existing_score:

                consolidated[key] = memory

        return list(
            consolidated.values()
        )
