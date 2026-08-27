from app.memory_constants import \
    MEMORY_STATUS_CANDIDATE


class MemoryCandidateService:

    def create_candidate(
        self,
        memory_item
    ):

        memory_item.status = (
            MEMORY_STATUS_CANDIDATE
        )

        return memory_item
