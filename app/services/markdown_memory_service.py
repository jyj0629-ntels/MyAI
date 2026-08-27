from app.repositories.markdown_memory_repository import \
    MarkdownMemoryRepository


class MarkdownMemoryService:

    def __init__(
        self,
        repository: MarkdownMemoryRepository
    ):
        self.repository = repository

    def save_memory(
        self,
        file_name: str,
        content: str
    ):
        return self.repository.write(
            file_name,
            content
        )

    def load_memory(
        self,
        file_name: str
    ):
        return self.repository.read(
            file_name
        )

    def exists(
        self,
        file_name: str
    ):
        return self.repository.exists(
            file_name
        )
