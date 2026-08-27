from app.models.conversation_memory import \
    ConversationMemory


class ConversationSummaryRepository:

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

    def save_summary(
        self,
        conversation_memory,
        summary: str
    ):

        conversation_memory.summary_md = (
            summary
        )

        self.db.commit()

        self.db.refresh(
            conversation_memory
        )

        return conversation_memory
