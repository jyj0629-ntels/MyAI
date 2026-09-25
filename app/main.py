import json
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text

from app.db.database import engine

from app.ai.models.request import AIRequest
from app.ai.services.registry import create_orchestrator

from app.personalization.services.prompt_builder import (
    PromptBuilder
)

from app.api.users import router as user_router
from app.api.ai import router as ai_router
from app.api.conversations import router as conversation_router
from app.api.memory import router as memory_router
from app.api.memory_item import router as memory_item_router
from app.api.markdown_memory import router as markdown_memory_router
from app.api.response_format_templates import router as response_format_templates_router
from app.api.forbidden_terms import router as forbidden_terms_router
from app.api.ai_dpi import router as ai_dpi_router
from app.db.base import Base
from app.db.database import engine
from app.models.ai_prompt_run import AIPromptRun
from app.models.chat_history import ChatHistory
from app.models.conversation import Conversation
from app.models.conversation_memory import ConversationMemory
from app.models.memory_item import MemoryItem
from app.models.response_format_template import ResponseFormatTemplate
from app.models.user import User
from app.models.forbidden_term import ForbiddenTerm


def ensure_database_schema():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as exc:
        print(f"[WARN] DB schema bootstrap failed: {exc}")
        return False


def seed_forbidden_terms():
    """demo_dpi 시연용 초기 금지어 시드. 이미 데이터가 있으면 건너뛴다."""
    try:
        from app.db.database import SessionLocal
        from app.repositories.forbidden_term_repository import ForbiddenTermRepository
        from app.models.forbidden_term import ForbiddenTerm

        default_terms = [
            {"term": "사내프로젝트명", "term_type": "WORD", "replacement_hint": "당사 내부 프로젝트", "category": "사내보안"},
            {"term": "내부서버주소", "term_type": "WORD", "replacement_hint": "사내 시스템", "category": "사내보안"},
            {"term": "고객사명", "term_type": "WORD", "replacement_hint": "특정 고객사", "category": "사내보안"},
        ]

        db = SessionLocal()
        try:
            repo = ForbiddenTermRepository(db)
            existing = repo.get_all(include_inactive=True)
            if existing:
                return
            for item in default_terms:
                repo.create(
                    ForbiddenTerm(
                        term=item["term"],
                        term_type=item["term_type"],
                        replacement_hint=item.get("replacement_hint"),
                        category=item.get("category"),
                        is_active=True,
                    )
                )
            print(f"[INFO] Seeded {len(default_terms)} forbidden terms.")
        finally:
            db.close()
    except Exception as exc:
        print(f"[WARN] forbidden term seed failed: {exc}")


ensure_database_schema()
seed_forbidden_terms()
prompt_builder = PromptBuilder()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="My AI Assistant",
    version="0.2.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


app.include_router(user_router)
app.include_router(ai_router)
app.include_router(conversation_router)
app.include_router(memory_router)
app.include_router(memory_item_router)

app.include_router(markdown_memory_router)
app.include_router(response_format_templates_router)
app.include_router(forbidden_terms_router)
app.include_router(ai_dpi_router)

orchestrator = create_orchestrator()

@app.get("/")
def root():

    return {
        "system": "My AI Assistant",
        "version": "0.2.0",
        "status": "OK",
    }


@app.get("/demo")
@app.get("/demo/")
@app.get("/ui")
@app.get("/ui/")
async def demo_ui():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/demo_dpi")
@app.get("/demo_dpi/")
async def demo_dpi_ui():
    return FileResponse(STATIC_DIR / "demo_dpi.html")


from app.services.provider_quota_service import ProviderQuotaService


@app.get("/ai/providers/status")
async def provider_status():
    try:
        providers = await ProviderQuotaService.get_status()
        return {
            "providers": providers,
            "note": "Public AI vendors do not provide a common quota API. Remaining quota is displayed only when the provider exposes it; otherwise the value is shown as unknown.",
        }
    except Exception as exc:
        return {
            "providers": [
                {"key": "gemini", "label": "Gemini", "quota": "unknown", "status": "unknown", "enabled": True},
                {"key": "openai", "label": "OpenAI", "quota": "unknown", "status": "unknown", "enabled": True},
                {"key": "groq", "label": "Groq", "quota": "unknown", "status": "unknown", "enabled": True},
                {"key": "mistral", "label": "Mistral", "quota": "unknown", "status": "unknown", "enabled": True},
                {"key": "meta", "label": "Meta AI", "quota": "unknown", "status": "unsupported", "enabled": False},
            ],
            "note": f"Provider quota lookup failed: {exc}",
        }


@app.get("/health")
def health():

    return {
        "status": "UP"
    }


@app.get("/health/db")
def health_db():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT 1")
        )

        value = result.scalar()

    return {
        "database": "UP",
        "result": value
    }

@app.post("/ai/ask", response_model=dict)
async def ask_ai(
    request: AIRequest = Body(
        ..., 
        description="Request payload for the AI assistant."
    ),
    http_request: Request = None
):

    try:
        content_type = http_request.headers.get("content-type", "").lower()
        payload = None

        if "application/json" in content_type:
            payload = await http_request.json()
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            form_data = await http_request.form()
            payload = {key: value for key, value in form_data.items()}
        else:
            raw_body = await http_request.body()
            if raw_body:
                try:
                    payload = json.loads(raw_body)
                except Exception:
                    payload = None

        if payload is None:
            payload = {key: value for key, value in http_request.query_params.items()}

        request_obj = AIRequest.from_payload(payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid request body: {str(exc)}") from exc

    request_obj = request
    provider = request_obj.provider or "mock"

    user_id = 1

    personalized_request = (
        prompt_builder.build(
            user_id=user_id,
            question=request_obj.question
        )
    )

    personalized_request.provider = provider

    try:

        response = await orchestrator.ask(
            provider,
            personalized_request
        )

        return {
            "request": {
                "original_question": request_obj.question,
                "provider": provider
            },
            "personalized_prompt": {
                "system_prompt":
                    personalized_request.system_prompt,

                "user_context":
                    personalized_request.user_context
            },
            "response": response
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
