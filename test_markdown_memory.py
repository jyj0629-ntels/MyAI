from app.repositories.markdown_memory_repository import \
    MarkdownMemoryRepository

from app.services.markdown_memory_service import \
    MarkdownMemoryService


service = MarkdownMemoryService(
    MarkdownMemoryRepository()
)

service.save_memory(
    "preferences.md",
    "# Preferences\n\n- 정확도 우선"
)

print(
    service.load_memory(
        "preferences.md"
    )
)

