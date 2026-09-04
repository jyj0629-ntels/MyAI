from app.ai.models.request import AIRequest


def test_ai_request_accepts_dynamic_question_from_payload():
    request = AIRequest.from_payload(
        {
            "user_id": 42,
            "question": "MyAI에게 추천 개발 프로세스를 알려줘.",
            "provider": "gemini",
        }
    )

    assert request.user_id == 42
    assert request.question == "MyAI에게 추천 개발 프로세스를 알려줘."
    assert request.provider == "gemini"


def test_ai_request_accepts_dynamic_question_from_form_values():
    request = AIRequest.from_payload(
        {
            "user_id": "7",
            "question": "개발 서버에서 어떤 설정을 먼저 확인해야 할까?",
            "prompt": "custom prompt",
        }
    )

    assert request.user_id == 7
    assert request.question == "개발 서버에서 어떤 설정을 먼저 확인해야 할까?"
    assert request.prompt == "custom prompt"
