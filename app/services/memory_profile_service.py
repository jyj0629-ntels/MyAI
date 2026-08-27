class MemoryProfileService:

    def build_profile(
        self,
        preferences: list[str],
        goals: list[str]
    ):

        profile = []

        if preferences:

            profile.append(
                "[Core Preferences]"
            )

            profile.extend(
                preferences
            )

        if goals:

            profile.append(
                "[User Goals]"
            )

            profile.extend(
                goals
            )

        return "\n".join(
            profile
        )
