from fastapi import APIRouter
from fastapi import Depends

from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse
from app.ai.services.registry import create_orchestrator
from app.ai.services.multi_provider_orchestrator import MultiProviderOrchestrator

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.repositories.chat_repository import ChatRepository
from app.repositories.memory_item_repository import MemoryItemRepository

from app.schemas.chat_history import ChatHistoryResponse

from app.services.chat_service import ChatService
from app.services.local_brain_service import LocalBrainService

from app.services.memory_item_service import MemoryItemService
from app.services.memory_context_service import MemoryContextService
from app.services.memory_retrieval_service import MemoryRetrievalService
from app.services.memory_query_service import MemoryQueryService

from app.services.prompt_trace_service import PromptTraceService

from app.services.context_package_service import ContextPackageService

from app.services.ai_prompt_run_service import AIPromptRunService

from app.services.conversation_memory_update_service import ConversationMemoryUpdateService
from app.services.conversation_memory_service import ConversationMemoryService

from app.services.memory_extraction_orchestrator import MemoryExtractionOrchestrator
from app.services.llm_memory_extraction_service import LLMMemoryExtractionService
from app.services.gemini_memory_extraction_provider import GeminiMemoryExtractionProvider
from app.services.chat_orchestrator_service import ChatOrchestratorService

from app.models.ai_prompt_run import AIPromptRun
from app.repositories.ai_prompt_run_repository import AIPromptRunRepository

from app.core.config import settings

import json

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

    projects = list(
        dict.fromkeys(
            [
                memory.content.strip()
                for memory in retrieved_memories
                if memory.type == "PROJECT"
            ]
        )
    )

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

    brain_result = await (
        brain.analyze(
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
    )

    print()
    print("# --------------------------------")
    print("# SELECTED PROVIDER")
    print("# --------------------------------")
    print(
        brain_result.provider
    )
    print("# --------------------------------")
    print()

    print("# --------------------------------")
    print("# TASK TYPE")
    print("# --------------------------------")
    print(
        brain_result.task_type
    )
    print("# --------------------------------")
    print()

    provider = (
        request.provider
        or brain_result.provider
    )

    prompt = (
        brain_result.prompt
    )

    trace = (
        PromptTraceService()
        .build_trace(
            provider=provider,
            task_type=brain_result.task_type,
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
    
    multi_result = await (
        MultiProviderOrchestrator(
            orchestrator.registry
        )
        .ask_all(
            request
        )
    )

    judge_request = (
        multi_result.get(
            "judge_request"
        )
    )

    selected = (
        multi_result[
            "selected"
        ]
    )

    judge_response = None

    if (
        judge_request
        and settings.ENABLE_LOCAL_CONSENSUS
    ):

        judge_response = await (
            orchestrator.ask(
                provider_name=
                settings.LOCAL_CONSENSUS_PROVIDER,
                request=judge_request
            )
        )

        print()
        print("# --------------------------------")
        print("# LOCAL CONSENSUS RESULT")
        print("# --------------------------------")
        print(
            judge_response.answer
        )
        print("# --------------------------------")
        print()



        judge_result = None 

        if judge_response:
        
            try:


                clean_json = (
                    judge_response.answer
                    .replace(
                        "```json",
                        ""
                    )
                    .replace(
                        "```",
                        ""
                    )
                    .strip()
                )

                judge_result = json.loads(
                    clean_json
                )


            except Exception as e:

                print()
                print("# --------------------------------")
                print("# JUDGE JSON PARSE ERROR")
                print("# --------------------------------")
                print(str(e))
                print("# --------------------------------")
                print()

    if not selected:

        response = await (
            orchestrator.ask(
                provider_name=provider,
                request=request
            )
        )

    else:

        response = AIResponse(
            provider=multi_result["responses"][0]["provider"],
            model=multi_result["responses"][0]["model"],
            answer=multi_result["responses"][0]["answer"],
            success=True
        )

        if judge_result:

            score = (
                judge_result.get(
                    "consensus_score",
                    0
                )
            )

            mode = "consensus"

            if (
                score
                < settings.CONSENSUS_THRESHOLD
            ):
                mode = "conflict"

            print()
            print("# --------------------------------")
            print("# JUDGE RESULT")
            print("# --------------------------------")
            print(
                f"mode={mode}"
            )
            print(
                f"score={score}"
            )
            print("# --------------------------------")
            print()

            final_answer = (
                judge_result.get(
                    "final_answer"
                )
            )

            if final_answer:

                if isinstance(
                    response,
                    dict
                ):

                    response["answer"] = (
                        final_answer
                    )

                else:

                    response.answer = (
                        final_answer
                    )

    await (
        ChatOrchestratorService()
        .post_process(
            request=request,
            response=response,
            db=db,
            memory_service=memory_service
        )
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
