import httpx

from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse

from app.core.config import settings


class OllamaProvider(
    AIProvider
):

    @property
    def name(self):

        return "ollama"

    async def ask(
        self,
        request: AIRequest
    ):

        try:

            async with httpx.AsyncClient(
                timeout=300
            ) as client:

                response = await (
                    client.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model":
                            settings.LOCAL_LLM_MODEL,
                            "prompt":
                            request.prompt
                            or request.question,
                            "stream": False
                        }
                    )
                )
                print()
                print("# --------------------------------")
                print("# OLLAMA HTTP STATUS")
                print("# --------------------------------")
                print(response.status_code)
                print("# --------------------------------")
                print()

                print()
                print("# --------------------------------")
                print("# OLLAMA RAW RESPONSE")
                print("# --------------------------------")
                print(response.text)
                print("# --------------------------------")
                print()

                data = response.json()

            return AIResponse(
                provider=self.name,
                model=settings.LOCAL_LLM_MODEL,
                answer=data["response"],
                success=True
            )

        except Exception as e:

            import traceback

            print()
            print("# --------------------------------")
            print("# OLLAMA ERROR")
            print("# --------------------------------")
            print(str(e))
            print("# --------------------------------")
            print()

            traceback.print_exc()

            return AIResponse(
                provider=self.name,
                model=settings.LOCAL_LLM_MODEL,
                answer="",
                success=False,
                error=str(e)
            )
