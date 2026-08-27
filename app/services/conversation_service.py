from app.repositories.conversation_repository import ConversationRepository


class ConversationService:

    def __init__(
        self,
        repository: ConversationRepository
    ):
        self.repository = repository

    def create(
        self,
        title: str
    ):
        return self.repository.create(title)

    def get_all(self):
        return self.repository.get_all()

    def get_by_id(
        self,
        conversation_id: int
    ):
        return self.repository.get_by_id(
            conversation_id
        )
