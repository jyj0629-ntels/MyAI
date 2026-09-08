import os

from dotenv import load_dotenv

load_dotenv()


def _is_placeholder_value(value):
    if value is None:
        return True

    normalized = str(value).strip()
    if not normalized:
        return True

    lowered = normalized.lower()
    placeholder_markers = (
        "your_",
        "placeholder",
        "changeme",
        "example",
        "test_",
        "dummy",
        "fill_me",
        "api_key_here",
        "not_configured",
        "<your",
    )

    return any(marker in lowered for marker in placeholder_markers)


class Settings:

    POSTGRES_HOST = os.getenv(
        "POSTGRES_HOST",
        "postgres"
    )

    POSTGRES_PORT = os.getenv(
        "POSTGRES_PORT",
        "5432"
    )

    POSTGRES_DB = os.getenv(
        "POSTGRES_DB",
        "myai"
    )

    POSTGRES_USER = os.getenv(
        "POSTGRES_USER",
        "myai"
    )

    POSTGRES_PASSWORD = os.getenv(
        "POSTGRES_PASSWORD",
        "wjddudwns.123"
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if _is_placeholder_value(GEMINI_API_KEY):
        GEMINI_API_KEY = None

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL"
    )

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if _is_placeholder_value(GROQ_API_KEY):
        GROQ_API_KEY = None

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL"
    )

    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    if _is_placeholder_value(MISTRAL_API_KEY):
        MISTRAL_API_KEY = None

    MISTRAL_MODEL = os.getenv(
        "MISTRAL_MODEL",
        "mistral-small-latest"
    )

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if _is_placeholder_value(DEEPSEEK_API_KEY):
        DEEPSEEK_API_KEY = None

    DEEPSEEK_MODEL = os.getenv(
        "DEEPSEEK_MODEL"
    )

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if _is_placeholder_value(OPENAI_API_KEY):
        OPENAI_API_KEY = None

    OPENAI_MODEL = os.getenv(
        "OPENAI_MODEL"
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

    PUBLIC_PROVIDERS = os.getenv(
        "PUBLIC_PROVIDERS",
        "gemini,groq,mistral"
    )

    LOCAL_BRAIN_DEFAULT_PROVIDER = os.getenv(
        "LOCAL_BRAIN_DEFAULT_PROVIDER",
        "ollama"
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
        "qwen3:14b"
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
            "600"
        )
    )

    OLLAMA_NUM_PREDICT = int(
        os.getenv(
            "OLLAMA_NUM_PREDICT",
            "1024"
        )
    )

    ENABLE_LOCAL_LLM_JUDGE = (
        os.getenv(
            "ENABLE_LOCAL_LLM_JUDGE",
            "false"
        ).lower() == "true"
    )

    LOCAL_LLM_FAST_PATH_ENABLED = (
        os.getenv(
            "LOCAL_LLM_FAST_PATH_ENABLED",
            "true"
        ).lower() == "true"
    )

    LOCAL_LLM_DEEP_ANALYSIS_ENABLED = (
        os.getenv(
            "LOCAL_LLM_DEEP_ANALYSIS_ENABLED",
            "true"
        ).lower() == "true"
    )

    LOCAL_LLM_FAST_PATH_MAX_CHARS = int(
        os.getenv(
            "LOCAL_LLM_FAST_PATH_MAX_CHARS",
            "120"
        )
    )

    MULTI_PROVIDER_EXCLUDE = os.getenv(
        "MULTI_PROVIDER_EXCLUDE",
        "ollama"
    )

settings = Settings()
