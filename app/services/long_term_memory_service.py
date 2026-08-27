from app.models.memory_item import MemoryItem


class LongTermMemoryService:

    def extract(
        self,
        user_id: int,
        summary: str
    ):

        memories = []

        text = summary.lower()

        if any(
            keyword in text
            for keyword in [ 
                "정확도",
                "정확한 답변",
                "빠른 답변보다 정확",
                "정확성을 선호"
            ]
        ):
            memories.append(
                MemoryItem(
                    user_id=user_id,
                    type="PREFERENCE",
                    key="answer_quality_priority",
                    content="사용자는 빠른 답변보다 정확한 답변을 선호한다.",
                    importance=0.95,
                    confidence=0.90,
                    freshness=1.0,
                    source_type="SUMMARY",
                    scope="USER",
                    status="CANDIDATE"
                )
            )

        return memories
