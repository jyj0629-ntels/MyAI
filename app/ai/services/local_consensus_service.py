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

아래 응답을 비교해 가장 적절한 답변을 고르고, 최종 응답은 사람이 읽기 쉬운 문장과 적절한 줄바꿈, 문단 구조를 갖춘 한국어로 작성하라.
- 절대로 긴 한 줄의 문장으로 이어붙이지 말 것
- 각 섹션은 줄바꿈으로 분리할 것
- 표/목록이 있으면 Markdown 형식으로 정리할 것
- 중복 내용을 제거하고 핵심만 남길 것
- final_answer는 사용자에게 바로 보여줄 수 있는 가독성 높은 형태여야 한다

{responses_block}

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
