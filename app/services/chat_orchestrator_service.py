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

        chat_service = (
            ChatService(
                ChatRepository(db)
            )
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

        if not request.conversation_id:
            return

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

        if not request.user_id:
            return

        summary = (
            ConversationMemoryService(
                db
            ).get_summary(
                request.conversation_id
            )
        )
        
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

        except Exception as e:

            print()
            print("# --------------------------------")
            print("# MEMORY EXTRACTION FAILED")
            print("# --------------------------------")
            print(str(e))
            print("# --------------------------------")
            print()

            return

        memories = await (
            MemoryExtractionOrchestrator(
                extractor
            )
            .process(
                user_id=request.user_id,
                summary=summary
            )
        )

        print()
        print("# --------------------------------")
        print("# MEMORY CANDIDATES")
        print("# --------------------------------")

        for memory in memories:

            print(memory.type)
            print(memory.key)
            print(memory.content)

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

            if (
                existing_memory
                or content_exists
            ):

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

        print("# --------------------------------")
        print()
