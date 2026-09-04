import asyncio

from app.services.local_brain_service import \
    LocalBrainService


async def main():

    brain = LocalBrainService()

    result = await brain.analyze(
        question="이 기술을 MyAI에 도입해도 될까?",
        user_profile="""
정확도 우선
유지보수성 중시
단계별 검증 선호
""",
        project_context=[
            "MyAI 개발중",
            "Memory Engine 구축중",
            "개인 AI 비서 완성"
        ]
    )

    print()
    print("# --------------------------------")
    print("# BRAIN RESULT")
    print("# --------------------------------")
    print(result)
    print("# --------------------------------")
    print()


asyncio.run(main())

