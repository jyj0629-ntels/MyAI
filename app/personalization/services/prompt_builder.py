from app.personalization.services.personalization_service import (
    PersonalizationService
)

from app.ai.models.request import AIRequest


class PromptBuilder:

    def __init__(self):

        self.personalization_service = (
            PersonalizationService()
        )

    def build(
        self,
        user_id: int,
        question: str
    ) -> AIRequest:

        personal_context = (
            self.personalization_service
            .build_context(user_id)
        )

        system_prompt = """
You are a personal AI assistant.

Always consider the user's personal context.

Do not unnecessarily repeat information.

Prefer concise and structured answers.

When useful, provide:
1. Key conclusion
2. Important reasons
3. Comparison
4. Recommendation
"""

        return AIRequest(
            question=question,
            system_prompt=system_prompt,
            user_context=personal_context,
            temperature=0.2
        )
