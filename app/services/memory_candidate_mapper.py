from app.models.memory_item import \
    MemoryItem


class MemoryCandidateMapper:

    def to_memory_item(
        self,
        user_id: int,
        candidate
    ):

        return MemoryItem(
            user_id=user_id,
            type=candidate.type,
            key=candidate.key,
            content=candidate.content,
            importance=candidate.importance,
            confidence=candidate.confidence,
            freshness=1.0,
            source_type="LOCAL_LLM",
            scope="USER",
            status="CANDIDATE"
        )
