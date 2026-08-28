from google import genai

from app.core.config import settings


class GeminiMemoryExtractionProvider:

    async def ask(
        self,
        prompt: str
    ):

        client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        result = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )

        return result.text
