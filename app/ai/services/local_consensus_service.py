from app.ai.models.request import AIRequest
from app.core.config import settings


class LocalConsensusService:

    def build_prompt(
        self,
        question,
        responses
    ):

        response_text = []

        for idx, item in enumerate(
            responses,
            start=1
        ):

            provider = item.get(
                "provider",
                ""
            )

            answer = item.get(
                "summary",
                item.get(
                    "answer",
                    ""
                )
            )

            response_text.append(
                f"""
[PROVIDER {idx}]
NAME:
{provider}

ANSWER:
{answer}
"""
            )

        responses_block = "\n".join(
            response_text
        )

        prompt = f"""
질문:
{question}

아래 여러 AI 응답을 비교 분석하라.

{responses_block}

반드시 JSON만 반환하라.

{{
  "mode":"consensus",
  "consensus_score":0,
  "common_claims":[],
  "conflicting_claims":[],
  "best_provider":"",
  "final_answer":""
}}
"""

        return prompt

    def build_request(
        self,
        question,
        responses
    ):

        prompt = (
            self.build_prompt(
                question,
                responses
            )
        )

        return AIRequest(
            question=prompt,
            provider=(
                settings.LOCAL_CONSENSUS_PROVIDER
            )
        )
