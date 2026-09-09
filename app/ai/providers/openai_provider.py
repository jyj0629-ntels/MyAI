import os

from openai import AsyncOpenAI

from app.core.config import settings, _is_placeholder_value
from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse


class OpenAIProvider(AIProvider):

    def __init__(self):

        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

        if not api_key or _is_placeholder_value(api_key):
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = AsyncOpenAI(
            api_key=api_key
        )

        self.model = (
            settings.OPENAI_MODEL
        )

    @property
    def name(self) -> str:

        return "openai"

    async def ask(
        self,
        request: AIRequest
    ) -> AIResponse:

        try:

            messages = []

            if request.system_prompt:

                messages.append(
                    {
                        "role": "system",
                        "content": request.system_prompt
                    }
                )

            user_content = request.question

            if request.user_context:

                user_content = (
                    f"{request.user_context}\n\n"
                    f"### USER QUESTION\n"
                    f"{request.question}"
                )

            messages.append(
                {
                    "role": "user",
                    "content": user_content
                }
            )

            def _log_attempt_error(attempt, max_attempts, error):
                print(f"[OPENAI ERROR] attempt={attempt}/{max_attempts} {error}")

            response = await self.call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=request.temperature
                ),
                on_attempt_error=_log_attempt_error
            )

            answer = response.choices[0].message.content or ""
            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "prompt_tokens", None)
            output_tokens = getattr(usage, "completion_tokens", None)

            return AIResponse(
                provider=self.name,
                model=self.model,
                answer=answer,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                success=True
            )

        except Exception as e:

            return AIResponse(
                provider=self.name,
                model=self.model,
                answer="",
                success=False,
                error=str(e)
            )
