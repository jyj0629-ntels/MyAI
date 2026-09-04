from fastapi import APIRouter, Body, Depends, HTTPException

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
from app.services.performance_tracker import PerformanceTracker

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
    payload: dict | None = Body(default=None),
    db: Session = Depends(get_db)
):
    tracker = PerformanceTracker()
    tracker.start("request_parse")

    try:
        request = AIRequest.from_payload(payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    tracker.finish("request_parse")

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
        tracker.start("memory_retrieval")
        retrieved_memories = (
            memory_query_service.query(
                user_id=request.user_id,
                question=request.question
            )
        )
        tracker.finish("memory_retrieval")

    print()
    print("# --------------------------------")
    print("# RAW DB HISTORY")
    print("# --------------------------------")
    for memory in retrieved_memories:
        print(f"type={memory.type} key={memory.key} content={memory.content}")
    print("# --------------------------------")
    print()

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

    tracker.start("context_package_build")
    context_package = (
        ContextPackageService()
        .build(
            preferences=preferences,
            goals=goals,
            projects=projects
        )
    )
    tracker.finish("context_package_build")

    print()
    print("# --------------------------------")
    print("# LEARNED USER PROFILE (LOCAL LLM SYNTHESIZED)")
    print("# --------------------------------")
    print(context_package.get("user_profile") or "(no learned user profile)")
    print("# --------------------------------")
    print()

    print()
    print("# --------------------------------")
    print("# PROJECT CONTEXT")
    print("# --------------------------------")
    print(context_package.get("project_context") or "(no project context)")
    print("# --------------------------------")
    print()

    brain = LocalBrainService()
    tracker.start("local_brain_analysis")
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
    tracker.finish("local_brain_analysis")

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

    available_providers = (
        orchestrator.registry.list()
    )

    available_providers = [
        item.lower()
        for item in available_providers
    ]

    if provider:

        provider = (
            provider.strip()
            .lower()
        )

    if (
        not provider
        or provider not in available_providers
    ):

        print()
        print("# --------------------------------")
        print("# INVALID PROVIDER")
        print("# --------------------------------")
        print(provider)
        print("# --------------------------------")
        print()

        provider = (
            settings.PRIMARY_PROVIDER
            .strip()
            .lower()
        )

    print()
    print("# --------------------------------")
    print("# BRAIN PROVIDER")
    print("# --------------------------------")
    print(brain_result.provider)
    print("# --------------------------------")
    print()

    print()
    print("# --------------------------------")
    print("# AVAILABLE PROVIDERS")
    print("# --------------------------------")
    print(available_providers)
    print("# --------------------------------")
    print()

    print()
    print("# --------------------------------")
    print("# FINAL PROVIDER")
    print("# --------------------------------")
    print(provider)
    print("# --------------------------------")
    print()

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
    
    tracker.start("provider_fanout")
    multi_result = await (
        MultiProviderOrchestrator(
            orchestrator.registry
        )
        .ask_all(
            request
        )
    )
    tracker.finish("provider_fanout")

    judge_request = (
        multi_result.get(
            "judge_request"
        )
    )

    selected = ( 
        multi_result.get(
            "selected"
        )
    )

    judge_result = None
    judge_response = None

    if (
        judge_request
        and settings.ENABLE_LOCAL_CONSENSUS
    ):
        tracker.start("local_consensus_judge")
        judge_response = await (
            orchestrator.ask(
                provider_name=
                settings.LOCAL_CONSENSUS_PROVIDER,
                request=judge_request
            )
        )
        tracker.finish("local_consensus_judge")

        print()
        print("# --------------------------------")
        print("# LOCAL CONSENSUS RESULT")
        print("# --------------------------------")
        print(
            judge_response.answer
        )
        print("# --------------------------------")
        print()

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
    
        responses = multi_result.get(
            "responses",
            []
        )

        if not responses:

            response = await (
                orchestrator.ask(
                    provider_name=provider,
                    request=request
                )
            )

        else:

            best_response = responses[0]

            response = AIResponse(
                provider=best_response["provider"],
                model=best_response["model"],
                answer=best_response["answer"],
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

            best_provider = (
                judge_result.get(
                    "best_provider"
                )
            )

            final_answer = (
                judge_result.get(
                    "final_answer"
                )
            )

            if best_provider:

                print()
                print("# --------------------------------")
                print("# JUDGE BEST PROVIDER")
                print("# --------------------------------")
                print(best_provider)
                print("# --------------------------------")
                print()

            if final_answer:
                response.answer = (
                    final_answer
                ) 
                
                if best_provider: 
                    for item in multi_result.get(
                        "responses", 
                        []
                    ):
                        if (
                            item["provider"]
                            .strip()
                            .lower()
                            ==
                            best_provider
                            .strip()
                            .lower()
                        ):
                            
                            response.provider = (
                                item["provider"]
                            )

                            response.model = (
                                item["model"]
                            )

                            break

    tracker.start("post_process")
    await (
        ChatOrchestratorService()
        .post_process(
            request=request,
            response=response,
            db=db,
            memory_service=memory_service
        )
    )
    tracker.finish("post_process")
    tracker.print_summary()

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
