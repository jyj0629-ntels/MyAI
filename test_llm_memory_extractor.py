import asyncio

from app.services.llm_memory_extraction_service import \
    LLMMemoryExtractionService


class FakeProvider:

    async def ask(
        self,
        prompt
    ):
        return """
{
  "memories": [
    {
      "type": "PREFERENCE",
      "key": "answer_quality_priority",
      "content": "사용자는 정확도를 우선한다.",
      "importance": 0.9,
      "confidence": 0.9
    }
  ]
}
"""


async def run():

    service = (
        LLMMemoryExtractionService(
            FakeProvider()
        )
    )

    result = await service.extract(
        "사용자는 정확한 답변을 선호한다."
    )

    print(
        result.memories[0].type
    )

    print(
        result.memories[0].key
    )


asyncio.run(run())
