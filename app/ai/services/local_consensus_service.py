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
- 절대로 여러 요약 문자열을 단순 합치거나 이어붙여서 final_answer를 만들지 말 것
- 반드시 각 공급자의 요약 내용을 읽고, 중복을 제거한 뒤 의미적으로 재구성해서 새 문장으로 작성할 것
- 각 섹션은 줄바꿈으로 분리할 것
- 표/목록이 있으면 Markdown 형식으로 정리할 것
- 중복 내용을 제거하고 핵심만 남길 것
- 최종 문서에서 중요한 사실만 남기고, 불필요한 서술/배경은 제거하라
- final_answer는 사용자에게 바로 보여줄 수 있는 가장 중요한 핵심 문구 중심으로 작성하라
- 각 항목의 핵심 특징만 남기고, 장황한 설명은 제외하라
- 동일한 문장이나 거의 같은 표현을 그대로 이어 붙이지 말고, 통합된 결론 문장으로 다시 작성하라

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

        request = AIRequest(
            question=prompt,
            provider=(
                settings.LOCAL_CONSENSUS_PROVIDER
            )
        )
        request.think = True
        return request
