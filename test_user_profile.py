from app.services.user_profile_service import \
    UserProfileService


profile = (
    UserProfileService()
    .build(
        preferences=[
            "정확도 우선",
            "단계별 검증 선호"
        ],
        goals=[
            "개인 AI 비서 플랫폼 구축"
        ]
    )
)

print(profile)
