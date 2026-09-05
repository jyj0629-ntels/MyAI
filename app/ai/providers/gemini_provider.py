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

            print()
            print("# --------------------------------")
            print("# GEMINI REQUEST")
            print("# --------------------------------")
            print(prompt)
            print("# --------------------------------")
            print()

            result = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )

            usage_metadata = getattr(result, "usage_metadata", None)
            input_tokens = None
            output_tokens = None

            if usage_metadata is not None:
                print(usage_metadata)
                input_tokens = getattr(usage_metadata, "prompt_token_count", None)
                output_tokens = getattr(usage_metadata, "candidates_token_count", None)

            print()
            print("# --------------------------------")
            print("# GEMINI RESPONSE")
            print("# --------------------------------")
            print(result.text)
            print("# --------------------------------")
            print()

            return AIResponse(
                provider=self.name,
                model=settings.GEMINI_MODEL,
                answer=result.text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
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
