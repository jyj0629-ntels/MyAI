from app.models.ai_prompt_run import AIPromptRun


class AIPromptRunRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        prompt_run: AIPromptRun
    ):

        self.db.add(prompt_run)

        self.db.commit()

        self.db.refresh(
            prompt_run
        )

        return prompt_run
