import os

from openai import AsyncOpenAI

from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse
from app.core.config import settings, _is_placeholder_value


class MistralProvider(AIProvider):

    def __init__(self):
        api_key = settings.MISTRAL_API_KEY or os.getenv("MISTRAL_API_KEY")
        if not api_key or _is_placeholder_value(api_key):
            raise RuntimeError("MISTRAL_API_KEY is not configured.")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1"
        )
        self.model = settings.MISTRAL_MODEL

    @property
    def name(self) -> str:
        return "mistral"

    async def _ask_once(self, request: AIRequest) -> AIResponse:
        try:
            messages = []

            if request.system_prompt:
                messages.append({
                    "role": "system",
                    "content": request.system_prompt,
                })

            user_content = request.question
            if request.user_context:
                user_content = (
                    f"{request.user_context}\n\n"
                    f"### USER QUESTION\n"
                    f"{request.question}"
                )

            messages.append({
                "role": "user",
                "content": user_content,
            })

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=getattr(request, "temperature", 0.7),
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
                success=True,
            )

        except Exception as e:
            return AIResponse(
                provider=self.name,
                model=self.model,
                answer="",
                success=False,
                error=str(e),
            )
