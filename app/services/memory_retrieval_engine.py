from app.services.relevant_memory_service import \
    RelevantMemoryService

from app.services.memory_consolidation_service import \
    MemoryConsolidationService


class MemoryRetrievalEngine:

    def __init__(self):

        self.relevant_service = (
            RelevantMemoryService()
        )

        self.consolidation_service = (
            MemoryConsolidationService()
        )

    def retrieve(
        self,
        question: str,
        memories
    ):

        relevant_memories = (
            self.relevant_service.filter(
                question,
                memories
            )
        )

        consolidated_memories = (
            self.consolidation_service
            .consolidate(
                relevant_memories
            )
        )

        return consolidated_memories
