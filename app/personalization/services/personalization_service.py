from app.personalization.repositories.memory_repository import (
    MemoryRepository
)


class PersonalizationService:

    def __init__(self):

        self.memory_repository = MemoryRepository()

    def build_context(self, user_id: int) -> str:

        memories = self.memory_repository.get_memories(
            user_id
        )

        if not memories:
            return ""

        lines = []

        lines.append(
            "### USER PERSONAL CONTEXT"
        )

        for memory in memories:

            lines.append(
                f"- {memory['memory_key']}: "
                f"{memory['memory_value']}"
            )

        return "\n".join(lines)
