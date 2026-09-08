from app.ai.services.local_consensus_service import LocalConsensusService
from app.ai.services.multi_provider_orchestrator import MultiProviderOrchestrator
from app.ai.services.response_summary_service import ResponseSummaryService
from app.services.performance_tracker import PerformanceTracker


def test_summary_keeps_important_points_only():
    answer = """
    ## Provider response
    안녕하세요. 저는 긴 설명을 많이 할 수 있습니다.
    여기에는 의미 없는 문장들이 많고, 사실상 중요하지 않습니다.
    SKT는 네트워크 안정성이 가장 좋다.
    KT는 유선 결합에 강하다.
    LG U+는 요금제 혜택이 좋아 보인다.
    이건 거의 쓰지 않는 장식 문장입니다.
    추천은 사용자의 우선순위를 기준으로 선택해야 한다.
    """

    summary = ResponseSummaryService().summarize(answer)

    assert "SKT는 네트워크 안정성이 가장 좋다" in summary
    assert "KT는 유선 결합에 강하다" in summary
    assert "LG U+는 요금제 혜택이 좋아 보인다" in summary
    assert "의미 없는 문장" not in summary
    assert "장식 문장" not in summary


def test_local_consensus_judge_uses_thinking_mode():
    req = LocalConsensusService().build_request(
        "어떤 통신사가 가장 좋나요?",
        [
            {"provider": "gemini", "answer": "SKT는 네트워크 안정성이 가장 좋다."},
            {"provider": "groq", "answer": "LG U+는 요금제가 가장 유리하다."},
        ],
    )

    assert req.think is True


def test_combined_summary_keeps_key_claims_without_truncating_from_end():
    responses = [
        {"provider": "gemini", "answer": "안녕하세요. SKT는 네트워크 안정성이 가장 좋다. KT는 유선 결합에 강하다. LG U+는 요금제 혜택이 가장 좋다."},
        {"provider": "groq", "answer": "안녕하세요. LG U+는 요금제 혜택이 좋다. SKT는 네트워크 품질이 좋다. KT는 브로드밴드가 강하다."},
    ]

    summary = MultiProviderOrchestrator.build_combined_summary(responses)

    assert "SKT" in summary
    assert "LG U+" in summary
    assert "네트워크" in summary
    assert "요금제" in summary
    assert "안녕하세요" not in summary


def test_ollama_thinking_is_not_exposed_as_final_answer():
    raw = {
        "response": "",
        "thinking": "Okay, this is internal reasoning that must not be shown to the user."
    }

    answer = raw.get("response") or ""
    assert answer == ""
    assert "internal reasoning" not in answer.lower()


def test_log_border_vary_by_step_type():
    request_border = PerformanceTracker.get_log_border("request")
    response_border = PerformanceTracker.get_log_border("response")
    consensus_border = PerformanceTracker.get_log_border("consensus")

    assert request_border != response_border
    assert response_border != consensus_border
    assert len(request_border) > 0
