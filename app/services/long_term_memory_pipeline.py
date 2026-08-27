from app.services.memory_candidate_pipeline import MemoryCandidatePipeline


class LongTermMemoryPipeline:

    def process(
        self,
        user_id: int,
        candidate_result
    ):

        return (
            MemoryCandidatePipeline()
            .process(
                user_id=user_id,
                candidates=candidate_result.memories
            )
        )
