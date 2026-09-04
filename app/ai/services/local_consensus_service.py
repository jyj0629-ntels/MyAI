from app.ai.models.request import AIRequest
from app.core.config import settings


class LocalConsensusService:

    def build_prompt(
        self,
        question,
        responses
    ):

        prompt = f"""
질문:
{question}

아래 AI 답변 요약을 비교하라.

JSON만 반환.

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

