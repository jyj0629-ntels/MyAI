from app.services.memory_candidate_pipeline import MemoryCandidatePipeline

class MemoryExtractionOrchestrator:

    def __init__(
        self,
        extractor
    ):
        self.extractor = extractor

    async def process(
        self,
        user_id: int,
        summary: str
    ):

        candidate_result = (
            await self.extractor.extract(
                summary
            )
        )

        memories = (
            MemoryCandidatePipeline()
            .process(
                user_id=user_id,
                candidates=candidate_result.memories
            )
        )

        return memories
