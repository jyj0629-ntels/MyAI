from app.services.preference_extraction_service import PreferenceExtractionService


def test_preference_extraction_is_not_purchase_specific():
    question = "오늘 고객 응답을 정리해 주고, 옵션별 장단점을 비교해줘"

    extracted = PreferenceExtractionService.extract(question)

    assert extracted
    assert "purchase" not in extracted[0]["key"].lower()
    assert "구매" not in extracted[0]["content"]
    assert "답변" in extracted[0]["content"]
