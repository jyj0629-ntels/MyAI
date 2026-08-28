from google import genai

from app.core.config import settings

from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse


class GeminiProvider(AIProvider):

    @property
    def name(self) -> str:
        return "gemini"

    async def ask(
        self,
        request: AIRequest
    ) -> AIResponse:

        client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        prompt = (
            request.prompt
            or request.question
        )

        if request.system_prompt:
            prompt = (
                f"{request.system_prompt}\n\n"
                f"{prompt}"
            )

        try:

            result = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )

            if hasattr(
                result,
                "usage_metadata"
            ):
                print(
                    result.usage_metadata
                )

            return AIResponse(
                provider=self.name,
                model=settings.GEMINI_MODEL,
                answer=result.text,
                success=True
            )

        except Exception as e:

            print(
                f"[GEMINI ERROR] {e}"
            )

            return AIResponse(
                provider=self.name,
                model=settings.GEMINI_MODEL,
                answer=f"[GEMINI ERROR] {str(e)}",
                success=False
            )
