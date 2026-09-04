import os

from app.core.config import settings

from groq import AsyncGroq

from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse

class GroqProvider(AIProvider):

    def __init__(self):

        self.client = AsyncGroq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
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

            response = await (
                self.client.chat.completions.create(
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
                )
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

            print(
                f"[GROQ SUCCESS] "
                f"{self.model}"
            )

            return AIResponse(
                provider=self.name,
                model=self.model,
                answer=answer,
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
