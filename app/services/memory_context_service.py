from app.services.memory_consolidation_service import \
    MemoryConsolidationService


class MemoryContextService:

    def __init__(self):

        self.consolidator = (
            MemoryConsolidationService()
        )

    def build_context(
        self,
        memories
    ):

        consolidated = (
            self.consolidator.consolidate(
                memories
            )
        )

        return [
            memory.content
            for memory in consolidated
        ]
