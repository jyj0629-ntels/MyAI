from app.services.context_builder_service import ContextBuilderService
from app.services.prompt_strategy_service import PromptStrategyService
from app.services.provider_selection_service import ProviderSelectionService
from app.services.local_brain_llm_service import LocalBrainLLMService

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

        self.llm_brain = (
            LocalBrainLLMService()
        )

    async def analyze(
        self,
        question: str,
        user_profile: str,
        project_context: list[str]
    ):

        return await (
            self.llm_brain.analyze(
                question=question,
                user_profile=user_profile,
                project_context=project_context
            )
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

        task_type = (
            self.provider_selector
            .classifier
            .classify(question)
        )

        role = "MyAI Assistant"

        if task_type == "ARCHITECTURE":
            role = "MyAI Architecture Reviewer"

        elif task_type == "CODING":
            role = "MyAI Senior Software Engineer"

        elif task_type == "DB":
            role = "MyAI Database Architect"

        prompt = (
            self.prompt_strategy.build(
                role=role,
                user_context=context,
                question=question
            )
        )

        provider = (
            self.provider_selector.select(
                question
            )
        )

        brain_request = (
            self.llm_brain.build_request(
                question=question,
                user_profile=user_profile,
                project_context=project_context
            )
        )

        print()
        print("# --------------------------------")
        print("# LLM BRAIN REQUEST LENGTH")
        print("# --------------------------------")
        print(len(brain_request.question))
        print("# --------------------------------")
        print()

        print("# --------------------------------")
        print("# LLM BRAIN REQUEST CREATED")
        print("# --------------------------------")
        print()

        return { 
            "provider": provider, 
            "task_type": task_type, 
            "prompt": prompt , 
            "brain_prompt": brain_request.question
        }
