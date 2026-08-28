import asyncio

from app.services.gemini_memory_extraction_provider import \
    GeminiMemoryExtractionProvider


async def run():

    provider = (
        GeminiMemoryExtractionProvider()
    )

    result = await (
        provider.ask(
            """
Return JSON.

{
  "memories": []
}
"""
        )
    )

    print(result)


asyncio.run(run())

