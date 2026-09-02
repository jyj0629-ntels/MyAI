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

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL"
    )

    DEEPSEEK_API_KEY = os.getenv(
        "DEEPSEEK_API_KEY"
    )

    DEEPSEEK_MODEL = os.getenv(
        "DEEPSEEK_MODEL"
    )

    CONSENSUS_THRESHOLD = int(
        os.getenv(
            "CONSENSUS_THRESHOLD",
            "80"
        )
    )

    PRIMARY_PROVIDER = os.getenv(
        "PRIMARY_PROVIDER",
        "gemini"
    )

    FALLBACK_PROVIDERS = os.getenv(
        "FALLBACK_PROVIDERS",
        "groq,openrouter,deepseek"
    )

    MIN_CONSENSUS_RESPONSES = int(
        os.getenv(
            "MIN_CONSENSUS_RESPONSES",
            "2"
        )
    )

    ALLOW_SINGLE_PROVIDER = (
        os.getenv(
            "ALLOW_SINGLE_PROVIDER",
            "true"
        ).lower() == "true"
    )

    ENABLE_LOCAL_CONSENSUS = (
        os.getenv(
            "ENABLE_LOCAL_CONSENSUS",
            "true"
        ).lower() == "true"
    )

    LOCAL_CONSENSUS_PROVIDER = os.getenv(
        "LOCAL_CONSENSUS_PROVIDER",
        "ollama"
    )

    ENABLE_CONFLICT_MODE = (
        os.getenv(
            "ENABLE_CONFLICT_MODE",
            "true"
        ).lower() == "true"
    )

    LOCAL_LLM_PROVIDER = os.getenv(
        "LOCAL_LLM_PROVIDER",
        "ollama"
    )

    LOCAL_LLM_MODEL = os.getenv(
        "LOCAL_LLM_MODEL",
        "qwen3:8b"
    )

    OLLAMA_HOST = os.getenv(
        "OLLAMA_HOST",
        "http://ollama:11434"
    )

    OLLAMA_GENERATE_URL = os.getenv(
        "OLLAMA_GENERATE_URL",
        f"{OLLAMA_HOST}/api/generate"
    )

    OLLAMA_TIMEOUT = int(
        os.getenv(
            "OLLAMA_TIMEOUT",
            "300"
        )
    )

    ENABLE_LOCAL_LLM_JUDGE = (
        os.getenv(
            "ENABLE_LOCAL_LLM_JUDGE",
            "true"
        ).lower() == "true"
    )

settings = Settings()
