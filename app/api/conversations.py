import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.repositories.conversation_repository import \
    ConversationRepository

from app.services.conversation_service import \
    ConversationService

from app.schemas.conversation import \
    ConversationCreate

from app.schemas.conversation import \
    ConversationResponse

from app.models.chat_history import ChatHistory
from app.repositories.chat_repository import ChatRepository
from app.services.chat_service import ChatService
from app.services.provider_response_storage_service import ProviderResponseStorageService

from app.schemas.chat_history import ChatHistoryResponse

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"]
)


@router.post(
    "/",
    response_model=ConversationResponse
)
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db)
):

    service = ConversationService(
        ConversationRepository(db)
    )

    return service.create(
        request.title
    )


@router.get(
    "/",
    response_model=list[ConversationResponse]
)
def get_conversations(
    db: Session = Depends(get_db)
):

    service = ConversationService(
        ConversationRepository(db)
    )

    return service.get_all()


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    service = ConversationService(
        ConversationRepository(db)
    )

    return service.get_by_id(
        conversation_id
    )

# --------------------------------------------------
# Conversation History
# --------------------------------------------------

@router.get(
    "/{conversation_id}/history",
    response_model=list[ChatHistoryResponse]
)
def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    service = ChatService(
        ChatRepository(db)
    )

    return service.get_conversation_history(
        conversation_id
    )


@router.get(
    "/{conversation_id}/history/{chat_id}/provider-responses"
)
def get_provider_responses_for_chat(
    conversation_id: int,
    chat_id: int,
    db: Session = Depends(get_db)
):
    chat = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == chat_id)
        .filter(ChatHistory.conversation_id == conversation_id)
        .first()
    )

    if chat is None:
        raise HTTPException(status_code=404, detail="chat history not found")

    if not chat.provider_response_path:
        return {"provider_responses": []}

    try:
        file_path = Path(chat.provider_response_path)
        if not file_path.exists():
            return {"provider_responses": []}

        markdown = file_path.read_text(encoding="utf-8")
        return {
            "provider_responses": ProviderResponseStorageService.parse_markdown_responses(markdown),
            "file_path": str(file_path)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"provider response file read failed: {str(exc)}") from exc
