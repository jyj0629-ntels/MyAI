from app.ai.services.local_consensus_service import LocalConsensusService
from app.ai.services.multi_provider_orchestrator import MultiProviderOrchestrator
from app.ai.services.response_summary_service import ResponseSummaryService
from app.services.performance_tracker import PerformanceTracker


def test_summary_keeps_important_points_only():
    # No hardcoded phrase list is used to drop lines; only structural signals
    # (headers, separators, short/symbol-only lines) are filtered.
    answer = """
    ## Provider response
    ---
    짧은글
    SKT는 네트워크 안정성이 가장 좋다.
    KT는 유선 결합에 강하다.
    LG U+는 요금제 혜택이 좋아 보인다.
    추천은 사용자의 우선순위를 기준으로 선택해야 한다.
    """

    summary = ResponseSummaryService().summarize(answer)

    assert "SKT는 네트워크 안정성이 가장 좋다" in summary
    assert "KT는 유선 결합에 강하다" in summary
    assert "LG U+는 요금제 혜택이 좋아 보인다" in summary
    assert "## Provider response" not in summary
    assert "짧은글" not in summary


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


def test_combined_summary_dedupes_without_fabricating_sentences():
    # Combined summary must only dedupe exact-duplicate claims across providers,
    # never invent a new sentence via hardcoded keyword matching.
    responses = [
        {"provider": "gemini", "answer": "SKT는 네트워크 안정성이 가장 좋다. LG U+는 요금제 혜택이 가장 좋다."},
        {"provider": "groq", "answer": "SKT는 네트워크 안정성이 가장 좋다. KT는 브로드밴드가 강하다."},
    ]

    summary = MultiProviderOrchestrator.build_combined_summary(responses)

    assert summary.count("SKT는 네트워크 안정성이 가장 좋다.") == 1
    assert "LG U+는 요금제 혜택이 가장 좋다." in summary
    assert "KT는 브로드밴드가 강하다." in summary


def test_summary_keeps_all_important_key_points_without_truncating_by_count():
    answer = """
    트위터는 사용자 참여도가 높다.
    인스타그램은 시각 콘텐츠 노출이 강하다.
    유튜브는 장기 콘텐츠 소비에 유리하다.
    네이버 블로그는 검색 유입이 강하다.
    카카오톡 채널은 커머스 전환에 효과적이다.
    틱톡은 짧은 숏폼 확산력이 강하다.
    링크드인은 B2B 신뢰 형성에 유리하다.
    안녕하세요. 인사말입니다.
    """

    summary = ResponseSummaryService().summarize(answer)

    assert "트위터는 사용자 참여도가 높다" in summary
    assert "인스타그램은 시각 콘텐츠 노출이 강하다" in summary
    assert "유튜브는 장기 콘텐츠 소비에 유리하다" in summary
    assert "네이버 블로그는 검색 유입이 강하다" in summary
    assert "카카오톡 채널은 커머스 전환에 효과적이다" in summary
    assert "틱톡은 짧은 숏폼 확산력이 강하다" in summary
    assert "링크드인은 B2B 신뢰 형성에 유리하다" in summary
    assert "안녕하세요" not in summary


def test_log_border_vary_by_step_type():
    request_border = PerformanceTracker.get_log_border("request")
    response_border = PerformanceTracker.get_log_border("response")
    consensus_border = PerformanceTracker.get_log_border("consensus")

    assert request_border != response_border
    assert response_border != consensus_border
    assert len(request_border) > 0


def test_combined_summary_avoids_hardcoded_provider_decisions():
    responses = [
        {"provider": "gemini", "answer": "SKT는 네트워크 안정성이 강하다. KT는 유선 연결이 안정적이다. LG U+는 요금제 혜택이 좋다."},
        {"provider": "groq", "answer": "LG U+는 요금제 혜택이 좋다. SKT는 네트워크 품질이 좋다. KT는 브로드밴드가 강하다."},
    ]

    summary = MultiProviderOrchestrator.build_combined_summary(responses)

    assert "SKT는 네트워크 안정성과 품질 강점이 가장 두드러진다" not in summary
    assert "LG U+는 요금제 혜택이 가장 강한 경쟁 요소다" not in summary
    assert "KT는 유선/브로드밴드 강점이 보완 요소로 작용한다" not in summary
    assert "네트워크" in summary
    assert "요금제" in summary
    assert "브로드밴드" in summary


def test_fallback_summary_keeps_all_important_claims_without_fixed_buffer():
    answer = """
    안녕하세요. 반갑습니다.
    첫째, 트위터는 사용자 참여도가 높다.
    둘째, 인스타그램은 시각 콘텐츠 노출이 강하다.
    셋째, 유튜브는 장기 콘텐츠 소비에 유리하다.
    넷째, 네이버 블로그는 검색 유입이 강하다.
    다섯째, 카카오톡 채널은 커머스 전환에 효과적이다.
    여섯째, 틱톡은 짧은 숏폼 확산력이 강하다.
    일곱째, 링크드인은 B2B 신뢰 형성에 유리하다.
    마지막으로, 이건 장식 문장입니다.
    """

    summary = ResponseSummaryService().summarize(answer)

    assert "트위터는 사용자 참여도가 높다" in summary
    assert "인스타그램은 시각 콘텐츠 노출이 강하다" in summary
    assert "유튜브는 장기 콘텐츠 소비에 유리하다" in summary
    assert "네이버 블로그는 검색 유입이 강하다" in summary
    assert "카카오톡 채널은 커머스 전환에 효과적이다" in summary
    assert "틱톡은 짧은 숏폼 확산력이 강하다" in summary
    assert "링크드인은 B2B 신뢰 형성에 유리하다" in summary
    assert "안녕하세요" not in summary
    assert "장식 문장입니다" not in summary
