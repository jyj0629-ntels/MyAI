class ResponseSummaryService:

    def summarize(
        self,
        answer: str
    ):

        if not answer:
            return ""

        answer = answer.strip()

        lines = []

        for line in answer.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("##"):
                continue

            if line.startswith("---"):
                continue

            if "------" in line:
                continue

            lines.append(
                line
            )

        summary = "\n".join(
            lines
        )

        max_length = 4000

        if len(summary) > max_length:

            summary = (
                summary[:max_length]
            )

        return summary
