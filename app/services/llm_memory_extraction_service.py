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

        print() 
        print("# --------------------------------") 
        print("# RAW MEMORY RESPONSE") 
        print("# --------------------------------") 
        print(response) 
        print("# --------------------------------") 
        print()

        try:

            cleaned_response = (
                response
                .replace(
                    "```json",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
                .strip()
            )

            return (
                MemoryCandidateResult
                .model_validate_json(
                    cleaned_response
                )
            )

        except Exception as e:

            print()
            print("# --------------------------------")
            print("# MEMORY PARSE ERROR")
            print("# --------------------------------")
            print(e)
            print("# --------------------------------")
            print()

            return (
                MemoryCandidateResult(
                    memories=[]
                )
            )
