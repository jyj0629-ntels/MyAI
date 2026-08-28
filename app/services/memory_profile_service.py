class MemoryProfileService:

    def build_profile(
        self,
        preferences: list[str],
        goals: list[str]
    ):

        profile = []

        if preferences:

            profile.extend(
                preferences
            )

        if goals:

            profile.extend(
                goals
            )

        return "\n".join(
            profile
        )
