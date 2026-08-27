class MemoryCandidateValidator:

    def validate(
        self,
        candidate
    ):

        if not candidate.content:
            return False

        if len(
            candidate.content.strip()
        ) < 10:
            return False

        if candidate.confidence < 0.5:
            return False

        return True
