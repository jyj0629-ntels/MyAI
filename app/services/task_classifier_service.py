class TaskClassifierService:

    def classify(
        self,
        question: str
    ):

        text = question.lower()

        if any(
            keyword in text
            for keyword in [
                "설계",
                "architecture",
                "아키텍처",
                "도입",
                "검토"
            ]
        ):
            return "ARCHITECTURE"

        if any(
            keyword in text
            for keyword in [
                "코드",
                "python",
                "fastapi",
                "api",
                "개발"
            ]
        ):
            return "CODE"

        return "GENERAL"
