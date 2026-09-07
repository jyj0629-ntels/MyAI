import json
from pathlib import Path

from app.services.provider_response_storage_service import ProviderResponseStorageService


class DummyDB:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def commit(self):
        pass

    def refresh(self, item):
        pass


def test_provider_response_storage_service_writes_markdown(tmp_path):
    service = ProviderResponseStorageService(base_dir=tmp_path)

    payload = [
        {"provider": "gemini", "model": "gemini-2.0", "answer": "Gemini raw answer"},
        {"provider": "openai", "model": "gpt-4o", "answer": "OpenAI raw answer"},
    ]

    file_path = service.write_markdown(conversation_id=123, provider_responses=payload)

    assert file_path.exists()
    text = file_path.read_text(encoding="utf-8")
    assert "Gemini" in text
    assert "Gemini raw answer" in text
    assert "OpenAI raw answer" in text


def test_provider_response_serialization_round_trip():
    payload = [
        {"provider": "gemini", "model": "gemini-2.0", "answer": "Gemini raw answer"},
    ]

    serialized = json.dumps(payload, ensure_ascii=False)
    restored = json.loads(serialized)

    assert restored[0]["provider"] == "gemini"
    assert restored[0]["answer"] == "Gemini raw answer"
