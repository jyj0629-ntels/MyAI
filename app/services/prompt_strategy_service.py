class PromptStrategyService:

    def build(
        self,
        user_context: str,
        question: str
    ):

        return f"""
[Role]
MyAI Architecture Reviewer

{user_context}

[Decision Criteria]
- 정확도 우선
- 유지보수성
- 기존 코드 최소 변경

[Task]
{question}

[Required Output]
- 분석
- 추천
- 근거
- 위험요소
"""
