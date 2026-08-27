from app.repositories.ai_prompt_run_repository import \
    AIPromptRunRepository


class AIPromptRunService:

    def __init__(
        self,
        repository: AIPromptRunRepository
    ):
        self.repository = repository

    def create(
        self,
        prompt_run
    ):
        return self.repository.create(
            prompt_run
        )
