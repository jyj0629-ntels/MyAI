from app.services.local_brain_llm_service import LocalBrainLLMService


def test_simple_question_uses_fast_path():
    service = LocalBrainLLMService()

    assert service.should_use_fast_path("오늘 날씨 어때?") is True
    assert service.should_use_fast_path("최근 프로젝트 일정과 진행 상황을 정리해서 제게 보여줘. 특히 리스크와 우선순위를 알려줘.") is False
