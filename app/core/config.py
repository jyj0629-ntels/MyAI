import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    DATABASE_URL = os.getenv(
        "DATABASE_URL"
    )

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL"
    )

    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY"
    )

    DEEPSEEK_API_KEY = os.getenv(
        "DEEPSEEK_API_KEY"
    )


settings = Settings()
