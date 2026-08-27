from app.repositories.conversation_memory_repository import ConversationMemoryRepository


class ConversationMemoryService:

    def __init__(
        self,
        db
    ):
        self.repository = (
            ConversationMemoryRepository(
                db
            )
        )

    def get_summary(
        self,
        conversation_id: int
    ):

        memory = (
            self.repository
            .get_by_conversation_id(
                conversation_id
            )
        )

        if not memory:
            return ""

        return (
            memory.summary_md
            or ""
        )
