from app.services.task_classifier_service import \
    TaskClassifierService


class ProviderSelectionService:

    def __init__(self):

        self.classifier = (
            TaskClassifierService()
        )

    def select(
        self,
        question: str
    ):

        task_type = (
            self.classifier.classify(
                question
            )
        )

        if task_type == "ARCHITECTURE":
            return "gemini"

        if task_type == "CODE":
            return "gemini"

        return "gemini"
