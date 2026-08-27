from app.services.memory_context_service import \
    MemoryContextService


class MemoryRetrievalService:

    def __init__(
        self,
        memory_service
    ):
        self.memory_service = (
            memory_service
        )

    def retrieve(
        self,
        user_id: int
    ):

        preference_items = (
            self.memory_service.get_by_type(
                user_id,
                "PREFERENCE"
            )
        )

        project_items = (
            self.memory_service.get_by_type(
                user_id,
                "PROJECT"
            )
        )

        goal_items = (
            self.memory_service.get_by_type(
                user_id,
                "GOAL"
            )
        )

        context_service = (
            MemoryContextService()
        )

        return {
            "preferences": (
                context_service.build_context(
                    preference_items
                )
            ),
            "projects": (
                context_service.build_context(
                    project_items
                )
            ),
            "goals": (
                context_service.build_context(
                    goal_items
                )
            )
        }
