from app.services.context_builder_service import \
    ContextBuilderService


service = ContextBuilderService()

context = service.build(
    preferences=[
        "정확도 우선",
        "단계별 검증 선호"
    ],
    projects=[
        "MyAI 개발중",
        "Memory Engine 구축중"
    ],
    goals=[
        "Android 앱 개발"
    ]
)

print(context)
