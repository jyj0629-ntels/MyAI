from app.models.memory_item import MemoryItem

from app.services.memory_consolidation_service import \
    MemoryConsolidationService


memory1 = MemoryItem(
    user_id=3,
    type="PREFERENCE",
    key="answer_quality_priority",
    content="사용자는 빠른 답변보다 정확한 답변을 우선한다.",
    confidence=0.85,
    importance=0.9,
    freshness=1.0,
    source_type="LOCAL_LLM",
    scope="USER"
)

memory2 = MemoryItem(
    user_id=3,
    type="PREFERENCE",
    key="answer_quality_priority",
    content="사용자는 빠른 답변보다 정확한 답변을 선호한다.",
    confidence=0.95,
    importance=0.9,
    freshness=1.0,
    source_type="LOCAL_LLM",
    scope="USER"
)

service = (
    MemoryConsolidationService()
)

result = service.consolidate(
    [
        memory1,
        memory2
    ]
)

print(len(result))

for item in result:
    print(item.key)
    print(item.content)
    print(item.confidence)
