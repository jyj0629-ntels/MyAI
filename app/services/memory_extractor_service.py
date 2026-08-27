from app.models.memory_item import MemoryItem


class MemoryExtractorService:

    def extract_preference_memory(
        self,
        user_id: int,
        content: str
    ):

        return MemoryItem(
            user_id=user_id,
            type="PREFERENCE",
            key="answer_quality_priority",
            content=content,
            importance=0.9,
            confidence=0.8,
            freshness=1.0,
            source_type="LOCAL_LLM",
            scope="USER",
            status="CANDIDATE"
        )
