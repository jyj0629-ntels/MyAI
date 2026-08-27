class PromptTraceService:

    def build_trace(
        self,
        provider: str,
        task_type: str,
        preferences: list[str],
        projects: list[str],
        goals: list[str]
    ):

        return {
            "provider": provider,
            "task_type": task_type,
            "preference_count": len(
                preferences
            ),
            "project_count": len(
                projects
            ),
            "goal_count": len(
                goals
            )
        }
