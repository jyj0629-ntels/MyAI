from app.services.memory_retrieval_engine import (
    MemoryRetrievalEngine
)


class MemoryQueryService:

    def __init__(
        self,
        memory_service
    ):
        self.memory_service = (
            memory_service
        )

        self.engine = (
            MemoryRetrievalEngine()
        )

    def query(
        self,
        user_id: int,
        question: str
    ):

        preferences = (
            self.memory_service.get_by_type(
                user_id,
                "PREFERENCE"
            )
        )

        goals = (
            self.memory_service.get_by_type(
                user_id,
                "GOAL"
            )
        )

        projects = (
            self.memory_service.get_by_type(
                user_id,
                "PROJECT"
            )
        )

        consolidated_preferences = (
            self.engine.consolidation_service
            .consolidate(
                preferences
            )
        )

        consolidated_goals = (
            self.engine.consolidation_service
            .consolidate(
                goals
            )
        )

        consolidated_projects = (
            self.engine.consolidation_service
            .consolidate(
                projects
            )
        )

        result = (
            consolidated_preferences
            + consolidated_goals
            + consolidated_projects
        )

        print()
        print("# --------------------------------")
        print("# MEMORY QUERY")
        print("# --------------------------------")
        print(
            f"user_id={user_id}"
        )
        print(
            f"question={question}"
        )
        print(
            f"preferences={len(consolidated_preferences)}"
        )
        print(
            f"goals={len(consolidated_goals)}"
        )
        print(
            f"projects={len(consolidated_projects)}"
        )
        print(
            f"total={len(result)}"
        )
        print("# --------------------------------")
        print()

        return result
