class ContextBuilderService:

    def build(
        self,
        user_profile: str,
        project_context: str
    ):

        sections = []

        sections.append(
            "##############################"
        )

        sections.append(
            "[User Context]"
        )

        sections.append(
            "##############################"
        )

        sections.append("")

        sections.append(
            "(1) Core Preferences"
        )

        sections.append(">")

        sections.append(user_profile)

        sections.append("")

        sections.append(
            "------------------------------"
        )

        sections.append("")

        sections.append(
            "(2) Project Context"
        )

        sections.append(">")

        sections.append(project_context)

        sections.append("")

        sections.append(
            "##############################"
        )

        return "\n".join(
            sections
        )
