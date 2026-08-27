from app.models.memory_item import MemoryItem

from app.services.memory_retrieval_engine import \
    MemoryRetrievalEngine


memories = [

    MemoryItem(
        user_id=3,
        type="PROJECT",
        key="myai_project",
        content="MyAI 프로젝트 진행중"
    ),

    MemoryItem(
        user_id=3,
        type="PROJECT",
        key="redis_project",
        content="Redis Cache 검토중"
    )
]

engine = (
    MemoryRetrievalEngine()
)

result = engine.retrieve(
    question="Redis를 사용할까?",
    memories=memories
)

print(len(result))

for item in result:
    print(item.key)
    print(item.content)
