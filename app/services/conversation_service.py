from app.repositories.conversation_repository import ConversationRepository


class ConversationService:

    def __init__(
        self,
        repository: ConversationRepository
    ):
        self.repository = repository

    def create(
        self,
        title: str,
        feature: str = "myai"
    ):
        return self.repository.create(title, feature)

    def get_all(self, feature: str | None = None):
        return self.repository.get_all(feature)

    def get_by_id(
        self,
        conversation_id: int
    ):
        return self.repository.get_by_id(
            conversation_id
        )
