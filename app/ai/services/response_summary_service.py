class ResponseSummaryService:

    def summarize(
        self,
        answer: str
    ):

        answer = answer.strip()

        lines = []

        for line in answer.splitlines():

            line = line.strip()

            if len(line) < 10:
                continue

            if line.startswith("##"):
                continue

            if line.startswith("---"):
                continue

            if "------" in line:
                continue

            lines.append(line)

            if len(lines) >= 20:
                break

        return "\n".join(lines)
