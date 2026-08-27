from app.services.conversation_summary_service import \
    ConversationSummaryService

from app.repositories.conversation_summary_repository import \
    ConversationSummaryRepository


class ConversationMemoryUpdateService:

    def __init__(
        self,
        db
    ):

        self.repository = (
            ConversationSummaryRepository(
                db
            )
        )

        self.summary_service = (
            ConversationSummaryService()
        )

    def update_summary(
        self,
        conversation_id: int,
        messages: list[str]
    ):

        memory = (
            self.repository
            .get_by_conversation_id(
                conversation_id
            )
        )

        if not memory:
            return None

        summary = (
            self.summary_service
            .summarize(messages)
        )

        return (
            self.repository
            .save_summary(
                memory,
                summary
            )
        )
