from app.models.memory_item import MemoryItem

from app.services.relevant_memory_service import \
    RelevantMemoryService


items = []

items.append(
    MemoryItem(
        user_id=3,
        type="PROJECT",
        key="myai_project",
        content="MyAI 프로젝트 진행중"
    )
)

items.append(
    MemoryItem(
        user_id=3,
        type="PROJECT",
        key="redis_project",
        content="Redis Cache 검토중"
    )
)

service = (
    RelevantMemoryService()
)

result = service.filter(
    "Redis를 사용할까?",
    items
)

print(
    len(result)
)

for item in result:
    print(item.content)
