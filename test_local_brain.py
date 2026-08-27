from app.services.local_brain_service import \
    LocalBrainService


brain = LocalBrainService()

prompt = brain.build_prompt(
    question="이 기술을 MyAI에 도입해도 될까?",
    preferences=[
        "정확도 우선",
        "유지보수성 중시",
        "단계별 검증 선호"
    ],
    projects=[
        "MyAI 개발중",
        "Memory Engine 구축중"
    ],
    goals=[
        "개인 AI 비서 완성"
    ]
)

print(prompt)
