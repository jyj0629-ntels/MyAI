from app.services.local_brain_llm_service import (
    LocalBrainLLMService
)


class LocalBrainService:

    def __init__(self):

        self.llm_brain = (
            LocalBrainLLMService()
        )

    async def analyze(
        self,
        question: str,
        user_profile: str,
        project_context: list[str]
    ):

        return await (
            self.llm_brain.analyze(
                question=question,
                user_profile=user_profile,
                project_context=project_context
            )
        )
