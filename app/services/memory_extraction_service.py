from app.models.memory_item import MemoryItem


class MemoryExtractionService:

    def extract(
        self,
        user_id: int,
        question: str,
        answer: str
    ):

        memories = []

        text = f"{question}\n{answer}"

        keywords = [
            "정확도",
            "정확한",
            "빠른 답변보다 정확"
        ]

        if any(
            keyword in text
            for keyword in keywords
        ):
            memories.append(
                MemoryItem(
                    user_id=user_id,
                    type="PREFERENCE",
                    key="answer_quality_priority",
                    content="사용자는 빠른 답변보다 정확한 답변을 선호한다.",
                    importance=0.95,
                    confidence=0.85,
                    freshness=1.0,
                    source_type="LOCAL_LLM",
                    scope="USER",
                    status="CANDIDATE"
                )
            )

        return memories
