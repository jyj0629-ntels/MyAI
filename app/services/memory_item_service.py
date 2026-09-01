from app.repositories.memory_item_repository import MemoryItemRepository
from difflib import SequenceMatcher


class MemoryItemService:

    def __init__(
        self,
        repository: MemoryItemRepository
    ):
        self.repository = repository

    def create(
        self,
        memory_item
    ):
        return self.repository.create(
            memory_item
        )

    def get_by_user(
        self,
        user_id: int
    ):
        return self.repository.get_by_user(
            user_id
        )

    def get_by_type(
        self,
        user_id: int,
        memory_type: str
    ):
        return self.repository.get_by_type(
            user_id,
            memory_type
        )

    def get_active_memories(
        self,
        user_id: int
    ):
        return self.repository.get_active_memories(
            user_id
        )

    def get_by_key(
        self,
        user_id: int,
        memory_key: str
    ):
        return self.repository.get_by_key(
            user_id,
            memory_key
        )

    def exists_by_key(
        self,
        user_id: int,
        memory_key: str
    ):
        return self.repository.exists_by_key(
            user_id,
            memory_key
        )

    def update(
        self,
        memory
    ):
        return self.repository.update(
            memory
        )

    def exists_similar_content(
        self,
        user_id: int,
        content: str,
        threshold: float = 0.80
    ):

        memories = self.get_by_user(
            user_id
        )

        target = (
            content.strip()
            .lower()
        )

        for memory in memories:
            existing = (
                memory.content
                .strip()
                .lower()
            )

            similarity = (
                SequenceMatcher(
                    None,
                    target,
                    existing
                ).ratio()
            )

            print(
                f"[SIMILARITY] "
                f"{similarity:.2f}"
            )

            if similarity >= threshold:
                return True

        return False
