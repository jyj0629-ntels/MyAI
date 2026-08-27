from app.models.memory_item import MemoryItem

from app.services.memory_validator_service import \
    MemoryValidatorService


memory = MemoryItem(
    user_id=3,
    type="PREFERENCE",
    key="answer_quality_priority",
    content="사용자는 정확도를 우선한다.",
    importance=0.95,
    confidence=0.92,
    freshness=1.0,
    source_type="LOCAL_LLM",
    scope="USER"
)

validator = MemoryValidatorService()

validated = validator.validate(
    memory
)

print(validated.status)
