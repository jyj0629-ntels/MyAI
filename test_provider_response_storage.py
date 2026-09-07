import json

from app.ai.models.response import AIResponse
from app.ai.services.response_collector import ResponseCollector
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


def test_provider_response_storage_includes_readable_summary_and_timing():
    service = ProviderResponseStorageService(base_dir="/tmp/provider_response_tests")
    payload = [{
        "provider": "gemini",
        "model": "gemini-2.0",
        "answer": "핵심 결론은 이 제품이 가성비가 좋다는 점입니다.\n\n근거: 성능 대비 가격이 우수합니다.",
        "summary": "핵심 결론: 가성비 우수\n근거: 성능 대비 가격이 우수",
        "response_time_ms": 482.5,
    }]

    text = service.format_markdown(conversation_id=99, provider_responses=payload)

    assert "응답 시간" in text
    assert "482.5ms" in text
    assert "핵심 결론" in text
    assert "근거" in text


def test_response_collector_preserves_provider_timing_metadata():
    responses = [
        AIResponse(
            provider="gemini",
            model="gemini-2.0",
            answer="핵심 결론은 가성비가 좋습니다.",
            success=True,
            response_time_ms=321.4,
        )
    ]

    collected = ResponseCollector().collect(responses)

    assert collected[0]["provider"] == "gemini"
    assert collected[0]["response_time_ms"] == 321.4
