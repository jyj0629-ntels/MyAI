from app.services.context_builder_service import ContextBuilderService
from app.services.prompt_strategy_service import PromptStrategyService
from app.services.provider_selection_service import ProviderSelectionService

class LocalBrainService:

    def __init__(self):

        self.context_builder = (
            ContextBuilderService()
        )

        self.prompt_strategy = (
            PromptStrategyService()
        )

        self.provider_selector = (
            ProviderSelectionService()
        )

    def build_prompt(
        self,
        question: str,
        user_profile: str,
        project_context: list[str]
    ):

        context = (
            self.context_builder.build(
                user_profile=user_profile,
                project_context=project_context
            )
        )

        prompt = (
            self.prompt_strategy.build(
                user_context=context,
                question=question
            )
        )

        task_type = ( 
            self.provider_selector 
            .classifier 
            .classify(question)
        )

        provider = (
            self.provider_selector.select(
                question
            )
        )

        return { 
            "provider": provider, 
            "task_type": task_type, 
            "prompt": prompt 
        }
