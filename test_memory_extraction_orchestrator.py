import asyncio

from app.services.fake_memory_llm_provider import FakeMemoryLLMProvider

from app.services.llm_memory_extraction_service import LLMMemoryExtractionService

from app.services.memory_extraction_orchestrator import MemoryExtractionOrchestrator


async def run():

    extractor = (
        LLMMemoryExtractionService(
            FakeMemoryLLMProvider()
        )
    )

    orchestrator = (
        MemoryExtractionOrchestrator(
            extractor
        )
    )

    memories = await (
        orchestrator.process(
            user_id=3,
            summary="""
            사용자는 정확한 답변을 선호한다.
            """
        )
    )

    print(len(memories))

    for item in memories:
        print(item.type)
        print(item.key)
        print(item.content)


asyncio.run(run())
