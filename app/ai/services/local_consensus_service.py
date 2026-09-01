from app.ai.models.request import AIRequest
from app.core.config import settings


class LocalConsensusService:

    def build_prompt(
        self,
        responses
    ):

        prompt = """
당신은 MyAI Consensus Judge 이다.

여러 AI의 답변을 비교 분석하라.

반드시 JSON 형식으로만 답변하라.

{
  "mode": "consensus",
  "consensus_score": 95,
  "consensus_reason": "",
  "common_claims": [],
  "conflicting_claims": [],
  "final_answer": ""
}

"""

        for response in responses:

            prompt += f"""

[{response['provider']}]

{response['answer']}

"""

        return prompt

    def build_request(
        self,
        responses
    ):

        prompt = (
            self.build_prompt(
                responses
            )
        )

        return AIRequest(
            question=prompt,
            provider=(
                settings.LOCAL_CONSENSUS_PROVIDER
            )
        )

