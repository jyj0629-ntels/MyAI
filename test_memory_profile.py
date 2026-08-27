from app.services.memory_profile_service import \
    MemoryProfileService


service = (
    MemoryProfileService()
)

profile = (
    service.build_profile(
        preferences=[
            "정확도 우선"
        ],
        goals=[
            "개인 AI 비서 플랫폼 완성"
        ]
    )
)

print(profile)
