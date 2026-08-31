from app.core.config import settings


class LocalConsensusService:

    def build_prompt(
        self,
        responses
    ):

        prompt = """
당신은 MyAI Consensus Judge 이다.

여러 AI 응답을 비교 분석하라.

반드시 JSON으로만 답변하라.

{
  "consensus_score": 0,
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
