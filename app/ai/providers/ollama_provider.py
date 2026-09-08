import httpx

from app.ai.providers.base import AIProvider
from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse

from app.core.config import settings
from app.services.performance_tracker import PerformanceTracker


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
            PerformanceTracker.print_section(
                "request",
                "OLLAMA REQUEST",
                f"model={settings.LOCAL_LLM_MODEL}\ntimeout={settings.OLLAMA_TIMEOUT}\nprompt_length={len(request.prompt or request.question)}"
            )
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
                PerformanceTracker.print_section(
                    "response",
                    "OLLAMA HTTP STATUS",
                    response.status_code
                )
                print()

                print()
                PerformanceTracker.print_section(
                    "response",
                    "OLLAMA RAW RESPONSE",
                    response.text
                )
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
