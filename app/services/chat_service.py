from app.repositories.chat_repository import ChatRepository


class ChatService:

    def __init__(
        self,
        repository: ChatRepository
    ):
        self.repository = repository

    def save_chat(
        self,
        conversation_id,
        provider,
        model,
        question,
        answer,
        input_tokens,
        output_tokens,
        success
    ):
        return self.repository.save(
            conversation_id,
            provider,
            model,
            question,
            answer,
            input_tokens,
            output_tokens,
            success
        )

    def get_recent_history(
        self,
        limit: int = 20
    ):
        return self.repository.get_recent(
            limit
        )

# --------------------------------------------------
# Conversation History
# --------------------------------------------------

    def get_conversation_history(
        self,
        conversation_id: int
    ):

        return self.repository.get_by_conversation_id(
            conversation_id
        )

    def get_recent_by_conversation(
        self,
        conversation_id: int,
        limit: int = 20
    ):
        return (
            self.repository
            .get_recent_by_conversation(
                conversation_id,
                limit
            )
        )
