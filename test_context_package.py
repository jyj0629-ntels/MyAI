from app.services.context_package_service import \
    ContextPackageService


result = (
    ContextPackageService()
    .build(
        preferences=[
            "정확도 우선"
        ],
        goals=[
            "개인 AI 비서 플랫폼 구축"
        ],
        projects=[
            "MyAI 프로젝트 진행중"
        ]
    )
)

print(result["user_profile"])

print()

print(result["project_context"])
