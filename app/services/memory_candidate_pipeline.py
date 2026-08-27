from app.services.memory_candidate_validator import \
    MemoryCandidateValidator

from app.services.memory_candidate_mapper import \
    MemoryCandidateMapper


class MemoryCandidatePipeline:

    def __init__(self):

        self.validator = (
            MemoryCandidateValidator()
        )

        self.mapper = (
            MemoryCandidateMapper()
        )

    def process(
        self,
        user_id: int,
        candidates
    ):

        memories = []

        for candidate in candidates:

            if not self.validator.validate(
                candidate
            ):
                continue

            memories.append(
                self.mapper.to_memory_item(
                    user_id,
                    candidate
                )
            )

        return memories
