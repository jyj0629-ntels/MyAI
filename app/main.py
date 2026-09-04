import json

from fastapi import FastAPI, HTTPException, Request

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

prompt_builder = PromptBuilder()

app = FastAPI(
    title="My AI Assistant",
    version="0.2.0",
)


app.include_router(user_router)
app.include_router(ai_router)
app.include_router(conversation_router)
app.include_router(memory_router)
app.include_router(memory_item_router)

app.include_router(
    markdown_memory_router
)

orchestrator = create_orchestrator()

@app.get("/")
def root():

    return {
        "system": "My AI Assistant",
        "version": "0.2.0",
        "status": "OK",
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

@app.post("/ai/ask")
async def ask_ai(http_request: Request):

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
