from app.services.user_profile_service import \
    UserProfileService

from app.services.project_context_service import \
    ProjectContextService


class ContextPackageService:

    def build(
        self,
        preferences: list[str],
        goals: list[str],
        projects: list[str]
    ):

        user_profile = (
            UserProfileService()
            .build(
                preferences=preferences,
                goals=goals
            )
        )

        project_context = (
            ProjectContextService()
            .build(
                projects
            )
        )

        return {
            "user_profile": user_profile,
            "project_context": project_context
        }
