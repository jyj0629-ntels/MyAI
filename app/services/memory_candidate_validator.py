class MemoryCandidateValidator:

    MEMORY_TYPES = {
        "PREFERENCE",
        "GOAL",
        "PROJECT",
        "INTEREST"
    }

    INVALID_KEYWORDS = [
        "에러",
        "오류",
        "error",
        "exception",
        "debug",
        "로그",
        "log",
        "traceback"
    ]

    def validate(
        self,
        candidate
    ):

        if not candidate:
            return False

        if not candidate.content:
            return False

        if not candidate.type:
            return False

        if candidate.type not in self.MEMORY_TYPES:
            return False

        content = (
            candidate.content
            .strip()
        )

        if len(content) < 10:
            return False

        if candidate.confidence < 0.50:
            return False

        content_lower = (
            content.lower()
        )

        for keyword in self.INVALID_KEYWORDS:

            if keyword in content_lower:
                return False

        if not candidate.key:
            return False

        key = (
            candidate.key
            .strip()
        )

        if len(key) < 3:
            return False

        return True

