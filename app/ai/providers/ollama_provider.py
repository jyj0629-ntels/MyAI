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

    @staticmethod
    def _resolve_num_predict(request: AIRequest) -> int:
        # Explicit per-request budget always wins (caller knows best).
        explicit = getattr(request, "max_tokens", None)
        if explicit:
            return int(explicit)

        # think=true spends part of the budget on hidden reasoning before the visible
        # answer. With the normal (small) budget the model can get cut off
        # (done_reason="length") having produced reasoning only, returning an empty
        # response. So think calls get the larger think-specific budget.
        if getattr(request, "think", False):
            return settings.OLLAMA_THINK_NUM_PREDICT

        return settings.OLLAMA_NUM_PREDICT

    async def _ask_once(
        self,
        request: AIRequest
    ):

        try:

            num_predict = self._resolve_num_predict(request)

            print()
            PerformanceTracker.print_section(
                "request",
                "OLLAMA REQUEST",
                f"model={settings.LOCAL_LLM_MODEL}\ntimeout={settings.OLLAMA_TIMEOUT}\nthink={getattr(request, 'think', False)}\nnum_predict={num_predict}\nprompt_length={len(request.prompt or request.question)}"
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
                                "num_predict": num_predict
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



            answer = (data.get("response") or "").strip()

            if not answer:
                done_reason = data.get("done_reason")
                had_thinking = bool((data.get("thinking") or "").strip())

                # A common failure mode with think=true: the model exhausted num_predict
                # on hidden reasoning (done_reason="length") and never wrote the visible
                # answer. Surface that clearly so callers/logs can act on it.
                if done_reason == "length" and had_thinking:
                    error_message = (
                        "Ollama produced only hidden reasoning and was cut off "
                        "(done_reason=length) before writing a visible answer. "
                        "Increase num_predict (e.g. OLLAMA_THINK_NUM_PREDICT) for think=true calls."
                    )
                else:
                    error_message = (
                        f"Ollama returned an empty response (done_reason={done_reason})."
                    )

                return AIResponse(
                    provider=self.name,
                    model=settings.LOCAL_LLM_MODEL,
                    answer="",
                    success=False,
                    error=error_message
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
