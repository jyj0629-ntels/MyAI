from app.models.memory_item import (
    MemoryItem
)


class MemoryCandidateMapper:

    def to_memory_item(
        self,
        user_id: int,
        candidate
    ):

        importance = max(
            0.0,
            min(
                float(
                    candidate.importance
                ),
                1.0
            )
        )

        confidence = max(
            0.0,
            min(
                float(
                    candidate.confidence
                ),
                1.0
            )
        )

        return MemoryItem(
            user_id=user_id,
            type=candidate.type.strip(),
            key=candidate.key.strip(),
            content=candidate.content.strip(),
            importance=importance,
            confidence=confidence,
            freshness=1.0,
            source_type="LOCAL_LLM",
            scope="USER",
            status="CANDIDATE"
        )
