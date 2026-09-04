import os

from openai import AsyncOpenAI

from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse


class OpenAIProvider(AIProvider):

    def __init__(self):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
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

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature
            )

            answer = response.choices[0].message.content or ""

            return AIResponse(
                provider=self.name,
                model=self.model,
                answer=answer,
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
