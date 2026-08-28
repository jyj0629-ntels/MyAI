class ProjectContextService:

    def build(
        self,
        projects: list[str]
    ):

        if not projects:
            return ""

        context = []

        context.extend(
            projects
        )

        return "\n".join(
            context
        )
