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
You are a personal AI assistant for this specific user.

Your job is to act as a trusted, long-term personal secretary.

Always consider the user's personal context, preferences, goals, and repeating behavior.
Do not ignore the user's personal memory when it is relevant.
Prefer concise, practical, and personally tailored answers.

When useful, provide:
1. Key conclusion
2. Why it matters to this user
3. Relevant comparison or tradeoff
4. Recommended action
5. Any warning or risk

Important rules:
- Use the user context as a primary filter.
- Avoid generic answers when personal context exists.
- If there is a conflicting recommendation, explain the tradeoff briefly.
- Keep the answer aligned to the user's values and patterns.
"""

        return AIRequest(
            question=question,
            system_prompt=system_prompt,
            user_context=personal_context,
            temperature=0.2
        )
