from app.models.memory_item import MemoryItem
from app.repositories.chat_repository import ChatRepository

from app.services.chat_service import ChatService
from app.services.conversation_memory_update_service import ConversationMemoryUpdateService
from app.services.conversation_memory_service import ConversationMemoryService
from app.services.memory_extraction_orchestrator import MemoryExtractionOrchestrator
from app.services.llm_memory_extraction_service import LLMMemoryExtractionService
from app.services.gemini_memory_extraction_provider import GeminiMemoryExtractionProvider


class ChatOrchestratorService:

    async def post_process(
        self,
        request,
        response,
        db,
        memory_service
    ):

        tracker = __import__("app.services.performance_tracker", fromlist=["PerformanceTracker"]).PerformanceTracker()
        tracker.start("conversation_save")

        chat_service = (
            ChatService(
                ChatRepository(db)
            )
        )

        try:
            chat_service.save_chat(
                conversation_id=request.conversation_id,
                provider=response.provider,
                model=response.model or response.provider or "unknown",
                question=request.question,
                answer=response.answer,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                success=response.success
            )
            tracker.finish("conversation_save", metadata={"conversation_id": request.conversation_id, "provider": response.provider, "success": bool(response.success)})
        except Exception as exc:
            tracker.finish("conversation_save", metadata={"conversation_id": request.conversation_id, "provider": response.provider, "success": False, "error": str(exc)})
            print(f"[WARN] chat history save failed: {exc}")

        if not request.conversation_id:
            return

        tracker.start("conversation_summary_build")
        history = (
            chat_service
            .get_recent_by_conversation(
                request.conversation_id,
                limit=20
            )
        )
        tracker.finish("conversation_summary_build", metadata={"conversation_id": request.conversation_id, "history_count": len(history)})

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

        if not request.user_id:
            return

        tracker.start("memory_extraction")
        summary = (
            ConversationMemoryService(
                db
            ).get_summary(
                request.conversation_id
            )
        )

        if not summary:
            tracker.finish("memory_extraction", metadata={"status": "skipped_empty_summary"})

            print()
            print("# --------------------------------")
            print("# EMPTY CONVERSATION SUMMARY")
            print("# --------------------------------")
            print("# MEMORY EXTRACTION SKIPPED")
            print("# --------------------------------")
            print()

            return
        
        extractor = (
            LLMMemoryExtractionService(
                GeminiMemoryExtractionProvider()
            )
        )

        try:

            memories = await (
                MemoryExtractionOrchestrator(
                    extractor
                )
                .process(
                    user_id=request.user_id,
                    summary=summary
                )
            )
            tracker.finish("memory_extraction", metadata={"status": "completed", "memory_count": len(memories)})

        except Exception as e:
            tracker.finish("memory_extraction", metadata={"status": "error", "error": str(e)})

            print()
            print("# --------------------------------")
            print("# MEMORY EXTRACTION FAILED")
            print("# --------------------------------")
            print(str(e))
            print("# --------------------------------")
            print()

            return

        tracker.start("memory_persist")
        for memory in memories:

            print()
            print("# --------------------------------") 
            print("# MEMORY CANDIDATE")
            print("# --------------------------------")
            print(
                f"type={memory.type}"
            )
            print(
                f"key={memory.key}"
            )
            print(
                f"content={memory.content}"
            )
            print("# --------------------------------")
            print()

            existing_memory = (
                memory_service.exists_by_key(
                    memory.user_id,
                    memory.key
                )
            )

            if existing_memory:

                print(
                    f"[MEMORY EXISTS] "
                    f"{memory.key}"
                )

                continue


            
            content_exists = (
                memory_service
                .exists_similar_content(
                    memory.user_id,
                    memory.content
                )
            )

            if existing_memory:

                print(
                    f"[MEMORY EXISTS] "
                    f"{memory.key}"
                )

                continue

            memory_service.create(
                memory
            )

            print(
                f"[MEMORY SAVED] "
                f"{memory.key}"
            )

        if getattr(response, "comparison", None) and request.user_id:
            score = float((response.comparison or {}).get("consensus_score", 0.0)) / 100.0
            if score >= 0.75:
                theme_key = f"theme_{abs(hash(request.question[:120]))}"
                memory = MemoryItem(
                    user_id=request.user_id,
                    type="PREFERENCE",
                    key=theme_key,
                    content=f"질문: {request.question[:180]} | 결론: {response.summary or response.answer[:300]} | 신뢰도: {score:.2f}",
                    importance=0.8,
                    confidence=score,
                    freshness=1.0,
                    source_type="conversation",
                    source_conversation_id=request.conversation_id,
                    source_chat_history_id=None,
                    scope="USER",
                    status="CANDIDATE"
                )
                if not memory_service.exists_by_key(request.user_id, memory.key):
                    memory_service.create(memory)
                    print(f"[MEMORY SAVED FROM COMPARISON] {memory.key} confidence={score:.2f}")

        tracker.finish("memory_persist", metadata={"saved_memory_count": len(memories)})
        print("# --------------------------------")
        print()
