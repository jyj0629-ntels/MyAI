from fastapi import FastAPI, HTTPException

from sqlalchemy import text

from app.db.database import engine

from app.ai.models.request import AIRequest
from app.ai.services.registry import create_orchestrator

from app.personalization.services.prompt_builder import (
    PromptBuilder
)

prompt_builder = PromptBuilder()

app = FastAPI(
    title="My AI Assistant",
    version="0.2.0",
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
async def ask_ai(request: AIRequest):

    provider = request.provider or "mock"

    user_id = 1

    personalized_request = (
        prompt_builder.build(
            user_id=user_id,
            question=request.question
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
                "original_question": request.question,
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
