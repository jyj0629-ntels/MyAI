from app.services.preference_extraction_service import PreferenceExtractionService
from app.services.memory_query_service import MemoryQueryService
from app.services.performance_tracker import PerformanceTracker


def test_extracts_purchase_preferences_from_question():
    question = (
        "토퍼를 구매해야하는데, 나는 하드하고 10만원대 가성비가 좋고, "
        "인터넷에 제품평이 좋고 많은 제품을 선호해. 항상 Top3 제품을 표로 "
        "만들어서 구매 링크포함해서 알려줘"
    )

    preferences = PreferenceExtractionService.extract(question)

    assert any("가성비" in item["content"] or "cost" in item["content"].lower() for item in preferences)
    assert any("Top3" in item["content"] or "top3" in item["content"].lower() for item in preferences)
    assert any("표" in item["content"] or "table" in item["content"].lower() for item in preferences)
    assert len(preferences) >= 3


def test_filters_purchase_preferences_out_of_dev_context():
    dev_memory = type("Memory", (), {"type": "PREFERENCE", "content": "AI 서비스 및 시스템 설계 시 속도보다 정확성을 우선시함"})()
    purchase_memory = type("Memory", (), {"type": "PREFERENCE", "content": "사용자는 구매 시 가성비와 후기 평판을 우선적으로 본다"})()

    filtered = MemoryQueryService.filter_relevant_memories(
        [dev_memory, purchase_memory],
        "토퍼를 구매해야 하는데 가성비와 후기 기준으로 Top3만 보여줘"
    )

    assert len(filtered) == 1
    assert "가성비" in filtered[0].content


def test_performance_tracker_numbers_stage_names():
    tracker = PerformanceTracker()
    tracker.start("1. user_context_analysis")
    tracker.finish("1. user_context_analysis")

    assert tracker.as_dict()["steps"][0]["name"].startswith("[STEP 1]")
