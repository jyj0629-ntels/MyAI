from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        title: str
    ):

        conversation = Conversation(
            title=title
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_all(self):

        return (
            self.db.query(Conversation)
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
