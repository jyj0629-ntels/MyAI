from app.models.memory_item import MemoryItem

from app.services.memory_confidence_service import \
    MemoryConfidenceService


memory = MemoryItem(
    user_id=3,
    type="PREFERENCE",
    key="answer_quality_priority",
    content="사용자는 정확도를 선호한다.",
    confidence=0.80
)

service = (
    MemoryConfidenceService()
)

updated = service.reinforce(
    memory
)

print(
    updated.confidence
)
