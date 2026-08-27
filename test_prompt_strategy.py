from app.services.prompt_strategy_service import \
    PromptStrategyService


service = PromptStrategyService()

prompt = service.build(
    user_context="""
정확도 우선
단계별 검증 선호
MyAI 개발중
""",
    question="Memory Engine 설계를 검토해줘"
)

print(prompt)
