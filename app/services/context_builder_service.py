class ContextBuilderService:

    def build(
        self,
        user_profile: str,
        project_context: str
    ):

        sections = []

        sections.append(
            "####### [User Context] #######"
        )
        sections.append("")
        sections.append(
            "(1) Core Preferences"
        )
        for line in user_profile.splitlines():
            if line.strip():
                sections.append(
                    f"  > {line}"
                )
        sections.append("------------------------------")
        sections.append("")
        sections.append(
            "(2) Project Context"
        )
        for line in project_context.splitlines():
            if line.strip():
                sections.append(
                    f"  > {line}"
                )
        sections.append(
            "##############################"
        )

        return "\n".join(
            sections
        )
