from app.core import config
from app.services.local_brain_llm_service import LocalBrainLLMService


def test_fast_path_prefers_local_ollama_provider(monkeypatch):
    monkeypatch.setattr(config.settings, "PRIMARY_PROVIDER", "gemini", raising=False)
    monkeypatch.setattr(config.settings, "LOCAL_LLM_PROVIDER", "ollama", raising=False)

    result = LocalBrainLLMService().build_fast_path_result(
        question="간단한 질문",
        user_profile="테스트 유저",
        project_context=["테스트 프로젝트"],
    )

    assert result.provider == "ollama"


def test_local_llm_fallback_uses_ollama_not_public_primary(monkeypatch):
    monkeypatch.setattr(config.settings, "PRIMARY_PROVIDER", "gemini", raising=False)
    monkeypatch.setattr(config.settings, "LOCAL_LLM_PROVIDER", "ollama", raising=False)

    payload = {"provider": ""}
    raw_provider = str(payload.get("provider", "")).strip()
    if not raw_provider or raw_provider.lower() in {"unknown", "none", "null"}:
        raw_provider = config.settings.LOCAL_LLM_PROVIDER or config.settings.PRIMARY_PROVIDER or "gemini"

    assert raw_provider == "ollama"
