from app.services.memory_profile_service import \
    MemoryProfileService


class UserProfileService:

    def build(
        self,
        preferences: list[str],
        goals: list[str]
    ):

        profile = (
            MemoryProfileService()
            .build_profile(
                preferences=preferences,
                goals=goals
            )
        )

        return profile
