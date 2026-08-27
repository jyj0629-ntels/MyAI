from app.models.conversation_memory import ConversationMemory


class ConversationMemoryRepository:

    def __init__(
        self,
        db
    ):
        self.db = db

    def get_by_conversation_id(
        self,
        conversation_id: int
    ):

        return (
            self.db.query(
                ConversationMemory
            )
            .filter(
                ConversationMemory.conversation_id
                == conversation_id
            )
            .first()
        )
