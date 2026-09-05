from app.models.chat_history import ChatHistory


class ChatRepository:

    def __init__(self, db):
        self.db = db

    def save(
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

        model_name = str(model or provider or "unknown").strip() or "unknown"

        chat = ChatHistory(
            conversation_id=conversation_id,
            provider=str(provider or "unknown").strip() or "unknown",
            model=model_name,
            question=question or "",
            answer=answer or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            success=success
        )

        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)

        return chat

    def get_recent(
        self,
        limit: int = 20
    ):

        return (
            self.db.query(ChatHistory)
            .order_by(ChatHistory.id.desc())
            .limit(limit)
            .all()
        )

# --------------------------------------------------
# Conversation History
# --------------------------------------------------

    def get_by_conversation_id(
        self,
        conversation_id: int
    ):

        return (
            self.db.query(ChatHistory)
            .filter(
                ChatHistory.conversation_id
                == conversation_id
            )
            .order_by(ChatHistory.id.asc())
            .all()
        )

    def get_recent_by_conversation(
        self,
        conversation_id: int,
        limit: int = 20
    ):

        return (
            self.db.query(
                ChatHistory
            )
            .filter(
                ChatHistory.conversation_id
                == conversation_id
            )
            .order_by(
                ChatHistory.id.desc()
            )
            .limit(limit)
            .all()
        )
