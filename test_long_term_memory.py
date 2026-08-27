from app.services.long_term_memory_service import \
    LongTermMemoryService

service = (
    LongTermMemoryService()
)

result = service.extract(
    user_id=3,
    summary="""
    사용자는 빠른 답변보다
    정확한 답변을 선호한다.
    """
)

print(len(result))

for item in result:
    print(item.type)
    print(item.key)
