import asyncio

from app.ai.models.request import AIRequest
from app.ai.providers.gemini_provider import GeminiProvider


async def main():

    provider = GeminiProvider()

    response = await provider.ask(
        AIRequest(
            question="안녕하세요. 자기소개 해주세요."
        )
    )

    print(response.model)
    print(type(response))
    print(response.answer) 
    if hasattr(response, "usage_metadata"):
        print(response.usage_metadata)


asyncio.run(main())
