class ConversationSummaryService:

    def summarize(
        self,
        messages: list[str]
    ):

        if not messages:
            return ""

        recent_messages = (
            messages[-10:]
        )

        return "\n".join(
            recent_messages
        )
