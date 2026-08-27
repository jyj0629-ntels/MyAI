import json

from app.schemas.memory_candidate_result import \
    MemoryCandidateResult

from app.services.memory_prompt_service import \
    MemoryPromptService


class LLMMemoryExtractionService:

    def __init__(
        self,
        llm_provider
    ):
        self.llm_provider = (
            llm_provider
        )

    async def extract(
        self,
        summary: str
    ):

        prompt = (
            MemoryPromptService()
            .build(summary)
        )

        response = await (
            self.llm_provider.ask(
                prompt
            )
        )

        try:

            return (
                MemoryCandidateResult
                .model_validate_json(
                    response
                )
            )

        except Exception:

            return (
                MemoryCandidateResult(
                    memories=[]
                )
            )
