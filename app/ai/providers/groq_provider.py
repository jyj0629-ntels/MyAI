import os

from app.core.config import settings, _is_placeholder_value

from groq import AsyncGroq

from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse

class GroqProvider(AIProvider):

    def __init__(self):

        api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key or _is_placeholder_value(api_key):
            raise RuntimeError("GROQ_API_KEY is not configured.")

        self.client = AsyncGroq(
            api_key=api_key
        )

        self.model = (
                settings.GROQ_MODEL
        )

    @property
    def name(self) -> str:

        return "groq"

    async def ask(
        self,
        request: AIRequest
    ) -> AIResponse:

        try:

            print() 
            print("# --------------------------------")

            print("# GROQ REQUEST")

            print("# --------------------------------")

            print(
                request.prompt
                or request.question
            )
            print("# --------------------------------")
            print()

            def _log_attempt_error(attempt, max_attempts, error):
                print(f"[GROQ ERROR] attempt={attempt}/{max_attempts} {error}")

            response = await self.call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": (
                                request.prompt
                                or request.question
                            )
                        }
                    ]
                ),
                on_attempt_error=_log_attempt_error
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            print()
            print("# --------------------------------")
            print("# GROQ RESPONSE")
            print("# --------------------------------")
            print(answer)
            print("# --------------------------------")
            print()

            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "prompt_tokens", None)
            output_tokens = getattr(usage, "completion_tokens", None)

            print(
                f"[GROQ SUCCESS] "
                f"{self.model}"
            )

            return AIResponse(
                provider=self.name,
                model=self.model,
                answer=answer,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                success=True
            )

        except Exception as e:

            print()
            print("# --------------------------------")
            print("# GROQ ERROR")
            print("# --------------------------------")
            print(str(e))
            print("# --------------------------------")
            print()

            return AIResponse(
                provider=self.name,
                model=self.model,
                answer="",
                success=False,
                error=str(e)
            )
