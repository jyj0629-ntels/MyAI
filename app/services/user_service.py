from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(
        self,
        repository: UserRepository
    ):
        self.repository = repository

    def create_user(
        self,
        email: str,
        name: str
    ):
        return self.repository.create(
            email=email,
            name=name
        )

    def get_user(
        self,
        email: str
    ):
        return self.repository.get_by_email(
            email=email
        )
