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

            print()
            print("# --------------------------------")
            print("# OLLAMA REQUEST")
            print("# --------------------------------")
            print(
                f"model={settings.LOCAL_LLM_MODEL}"
            )
            print(
                f"timeout={settings.OLLAMA_TIMEOUT}"
            )
            print(
                f"prompt_length="
                f"{len(request.prompt or request.question)}"
            )
            print("# --------------------------------")
            print()


            async with httpx.AsyncClient(
		        timeout=settings.OLLAMA_TIMEOUT
            ) as client:

                response = await (
                    client.post(
			            settings.OLLAMA_GENERATE_URL,
                        json={
                            "model": settings.LOCAL_LLM_MODEL,
                            "prompt": request.prompt or request.question,
                            "stream": False,
                            "think": getattr(
                                request,
                                "think",
                                False
                            ),
                            "options": {
                                "num_predict": 320
                            }
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



            answer = (
                data.get("response")
                or ""
            )

            if not answer:

                answer = (
                    data.get("thinking")
                    or ""
                )

            return AIResponse(
                provider=self.name,
                model=settings.LOCAL_LLM_MODEL,
                answer=answer,
                success=True
            )

        except Exception as e:

            import traceback

            print()
            print("# --------------------------------")
            print("[ERROR] OLLAMA ERROR")
            print("# --------------------------------")
            print(str(e))
            print(repr(e))
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
