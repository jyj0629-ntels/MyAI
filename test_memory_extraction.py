from app.services.memory_extraction_service import \
    MemoryExtractionService


service = MemoryExtractionService()

memories = service.extract(
    user_id=3,
    question="속도보다 정확도가 중요해",
    answer="정확도를 우선해야 합니다."
)

print(
    len(memories)
)

for memory in memories:

    print(memory.type)
    print(memory.key)
    print(memory.content)
