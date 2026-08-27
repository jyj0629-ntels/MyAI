from fastapi import APIRouter
from fastapi import Depends

from app.ai.models.request import AIRequest
from app.ai.services.registry import create_orchestrator

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.repositories.chat_repository import ChatRepository
from app.repositories.memory_item_repository import MemoryItemRepository

from app.schemas.chat_history import ChatHistoryResponse

from app.services.chat_service import ChatService
from app.services.local_brain_service import LocalBrainService

from app.services.memory_item_service import MemoryItemService
from app.services.memory_extraction_service import MemoryExtractionService
from app.services.memory_context_service import MemoryContextService
from app.services.memory_retrieval_service import MemoryRetrievalService
from app.services.memory_query_service import MemoryQueryService
from app.services.memory_confidence_service import MemoryConfidenceService

from app.services.prompt_trace_service import PromptTraceService

from app.services.context_package_service import ContextPackageService

from app.services.ai_prompt_run_service import AIPromptRunService

from app.services.conversation_memory_update_service import ConversationMemoryUpdateService
from app.services.conversation_memory_service import ConversationMemoryService

from app.services.long_term_memory_service import LongTermMemoryService
from app.services.memory_extraction_orchestrator import MemoryExtractionOrchestrator
from app.services.llm_memory_extraction_service import LLMMemoryExtractionService
from app.services.fake_memory_llm_provider import FakeMemoryLLMProvider
from app.services.chat_orchestrator_service import ChatOrchestratorService

from app.models.ai_prompt_run import AIPromptRun
from app.repositories.ai_prompt_run_repository import AIPromptRunRepository


router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

orchestrator = create_orchestrator()


@router.post("/chat")
async def chat(
    request: AIRequest,
    db: Session = Depends(get_db)
):

    provider = (
        request.provider
        or "gemini"
    )

    memory_service = MemoryItemService(
        MemoryItemRepository(db)
    )

    memory_query_service = (
        MemoryQueryService(
            memory_service
        )
    )

    retrieved_memories = []

    if request.user_id:

        retrieved_memories = (
            memory_query_service.query(
                user_id=request.user_id,
                question=request.question
            )
        )

    preferences = [
        memory.content
        for memory in retrieved_memories
        if memory.type == "PREFERENCE"
    ]

    projects = [
        memory.content
        for memory in retrieved_memories
        if memory.type == "PROJECT"
    ]

    goals = [
        memory.content
        for memory in retrieved_memories
        if memory.type == "GOAL"
    ]

    context_package = ( 
        ContextPackageService()
        .build(
            preferences=preferences,
            goals=goals,
            projects=projects
        )
    )

    brain = LocalBrainService()

    brain_result = brain.build_prompt(
        question=request.question,
        user_profile=(
            context_package[
                "user_profile"
            ]
        ),
        project_context=(
            context_package[
                "project_context"
            ]
        )
    )

    print()

    print("# --------------------------------")
    print("# SELECTED PROVIDER")
    print("# --------------------------------")
    print(
        brain_result["provider"]
    )
    print("# --------------------------------")
    print()

    print("# --------------------------------")
    print("# TASK TYPE")
    print("# --------------------------------")
    print(
        brain_result["task_type"]
    )
    print("# --------------------------------")
    print()

    provider = (
        request.provider
        or brain_result["provider"]
    )

    prompt = (
        brain_result["prompt"]
    )

    trace = (
        PromptTraceService()
        .build_trace(
            provider=provider,
            task_type=brain_result["task_type"],
            preferences=preferences,
            projects=projects,
            goals=goals
        )
    )

    print()

    print("# --------------------------------")
    print("# PROMPT TRACE")
    print("# --------------------------------")

    print(trace)

    print("# --------------------------------")
    print()

    request.prompt = prompt

    prompt_run_service = ( 
        AIPromptRunService(
            AIPromptRunRepository(db)
        )
    )

    prompt_run_service.create(
        AIPromptRun(
            conversation_id=request.conversation_id,
            selected_provider=provider,
            selected_model=None,
            strategy_md="Local Brain Prompt Strategy",
            final_prompt=prompt
        )
    )

    print()
    print("# --------------------------------")
    print("# LOCAL BRAIN GENERATED PROMPT")
    print("# --------------------------------")
    print(prompt)
    print("# --------------------------------")
    print()
    
    response = await orchestrator.ask(
        provider_name=provider,
        request=request
    )

    chat_service = ChatService(
        ChatRepository(db)
    )

    if request.user_id:

        extractor = (
            MemoryExtractionService()
        )

        extracted_memories = (
            extractor.extract(
                user_id=request.user_id,
                question=request.question,
                answer=response.answer
            )
        )

        for memory in extracted_memories:

            existing_memory = (
                memory_service.exists_by_key(
                    memory.user_id,
                    memory.key
                )
            )

            if existing_memory:
    
                updated_memory = ( 
                    MemoryConfidenceService() 
                    .reinforce( 
                        existing_memory
                    )
            )

            memory_service.update(
                updated_memory
            )

            print(
                f"[MEMORY REINFORCED] "
                f"{memory.key} "
                f"confidence="
                f"{updated_memory.confidence}"
            )

            continue

        memory_service.create(
            memory
        )

        print(
            f"[MEMORY CREATED] "
            f"{memory.type} : "
            f"{memory.content}"
        )

    chat_service.save_chat(
        conversation_id=request.conversation_id,
        provider=response.provider,
        model=response.model,
        question=request.question,
        answer=response.answer,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        success=response.success
    )

    if request.conversation_id:

        history = (
            chat_service
            .get_recent_by_conversation(
                request.conversation_id,
                limit=20
            )
        )

        messages = []

        for item in reversed(history):

            messages.append(
                f"Q: {item.question}"
            )

            messages.append(
                f"A: {item.answer}"
            )

        ConversationMemoryUpdateService(
            db
        ).update_summary(
            conversation_id=request.conversation_id,
            messages=messages
        )

        if (
            request.user_id 
            and request.conversation_id
        ):
    
            summary = (
                ConversationMemoryService(
                    db
                ).get_summary( 
                    request.conversation_id
                )
            )

            extractor = (
                LLMMemoryExtractionService( 
                    FakeMemoryLLMProvider()
                )
            )

            memories = await ( 
                MemoryExtractionOrchestrator (
                    extractor
                )
                .process(
                    user_id=request.user_id,
                    summary=summary
                )
            )

            for memory in memories: 

                print(memory.type)
                print(memory.key)
                print(memory.content)
                print()

            print("# --------------------------------")
            print()

            for memory in memories:

                existing_memory = (
                    memory_service.exists_by_key(
                        memory.user_id,
                        memory.key
                    )
                )
                if existing_memory:
                    continue
            
                memory_service.create(
                    memory
                )

                print(
                    f"[LONG TERM MEMORY CREATED] "
                    f"{memory.key}"
                )

    return response

@router.get(
    "/history",
    response_model=list[ChatHistoryResponse]
)
def get_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):

    service = ChatService(
        ChatRepository(db)
    )

    return service.get_recent_history(
        limit
    )
