class MemoryConfidenceService:

    def reinforce(
        self,
        existing_memory,
        increment: float = 0.05
    ):

        current = (
            existing_memory.confidence
            or 0.0
        )

        updated = min(
            current + increment,
            1.0
        )

        existing_memory.confidence = (
            updated
        )

        return existing_memory
