from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        title: str,
        feature: str = "myai"
    ):

        conversation = Conversation(
            title=title,
            feature=(feature or "myai")
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_all(self, feature: str | None = None):

        query = self.db.query(Conversation)
        if feature:
            query = query.filter(Conversation.feature == feature)
        return (
            query
            .order_by(Conversation.id.desc())
            .all()
        )

    def get_by_id(
        self,
        conversation_id: int
    ):

        return (
            self.db.query(Conversation)
            .filter(
                Conversation.id == conversation_id
            )
            .first()
        )
