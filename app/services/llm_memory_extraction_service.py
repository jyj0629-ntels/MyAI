import json
import re

from app.schemas.memory_candidate_result import (
    MemoryCandidateResult
)

from app.services.memory_prompt_service import (
    MemoryPromptService
)


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
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            match = re.search(
                r"\{.*\}",
                cleaned_response,
                re.DOTALL
            )

            if not match:

                raise ValueError(
                    "JSON block not found"
                )

            json_text = (
                match.group(0)
            )

            print()
            print("# --------------------------------")
            print("# MEMORY JSON")
            print("# --------------------------------")
            print(json_text)
            print("# --------------------------------")
            print()

            return (
                MemoryCandidateResult
                .model_validate_json(
                    json_text
                )
            )

        except Exception as e:

            print()
            print("# --------------------------------")
            print("# MEMORY PARSE ERROR")
            print("# --------------------------------")
            print(str(e))
            print("# --------------------------------")
            print()

            return (
                MemoryCandidateResult(
                    memories=[]
                )
            )
