from app.services.memory_extractor_service import \
    MemoryExtractorService


service = MemoryExtractorService()

memory = service.extract_preference_memory(
    user_id=3,
    content="사용자는 빠른 답변보다 정확한 답변을 선호한다."
)

print(memory.type)
print(memory.key)
print(memory.status)
print(memory.content)
