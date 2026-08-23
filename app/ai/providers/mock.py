from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse


class MockProvider(AIProvider):

    @property
    def name(self) -> str:
        return "mock"

    async def ask(
        self,
        request: AIRequest
    ) -> AIResponse:

        return AIResponse(
            provider=self.name,
            model="mock-model",
            answer=(
                f"[MOCK AI RESPONSE] "
                f"Question: {request.question}"
            ),
            success=True
        )
