from app.services.preference_extraction_service import PreferenceExtractionService


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
