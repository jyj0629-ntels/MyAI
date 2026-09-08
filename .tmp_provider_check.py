import asyncio
import os
from app.core.config import settings
from app.ai.models.request import AIRequest
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.providers.mistral_provider import MistralProvider

print('CHECK_ENV')
print('GEMINI_KEY_SET', bool(settings.GEMINI_API_KEY))
print('GROQ_KEY_SET', bool(settings.GROQ_API_KEY))
print('MISTRAL_KEY_SET', bool(settings.MISTRAL_API_KEY))
print('MISTRAL_MODEL', settings.MISTRAL_MODEL)

async def probe(name, provider):
    try:
        result = await provider.ask(AIRequest(question='hello', system_prompt='Reply only with OK', user_context=''))
        print(name, 'SUCCESS', result.success)
        print(name, 'ERROR', result.error)
        print(name, 'ANSWER_PREFIX', (result.answer or '')[:120].replace('\n', ' '))
    except Exception as e:
        print(name, 'EXCEPTION', type(e).__name__, str(e)[:200])

async def main():
    await probe('gemini', GeminiProvider())
    await probe('groq', GroqProvider())
    await probe('mistral', MistralProvider())

asyncio.run(main())
