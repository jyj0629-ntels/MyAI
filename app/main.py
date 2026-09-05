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
from app.db.base import Base
from app.db.database import engine
from app.models.ai_prompt_run import AIPromptRun
from app.models.chat_history import ChatHistory
from app.models.conversation import Conversation
from app.models.conversation_memory import ConversationMemory
from app.models.memory_item import MemoryItem
from app.models.response_format_template import ResponseFormatTemplate
from app.models.user import User


def ensure_database_schema():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as exc:
        print(f"[WARN] DB schema bootstrap failed: {exc}")
        return False


ensure_database_schema()
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

orchestrator = create_orchestrator()

@app.get("/")
def root():

    return {
        "system": "My AI Assistant",
        "version": "0.2.0",
        "status": "OK",
    }


@app.get("/demo")
@app.get("/ui")
async def demo_ui():
    return FileResponse(STATIC_DIR / "index.html")


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
