from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.repositories.conversation_memory_repository import ConversationMemoryRepository

from app.services.conversation_memory_service import ConversationMemoryService

from app.schemas.conversation_memory import ConversationMemoryCreate

from app.schemas.conversation_memory import ConversationMemoryResponse


router = APIRouter(
    prefix="/memory",
    tags=["memory"]
)


@router.post(
    "/conversation",
    response_model=ConversationMemoryResponse
)
def create_conversation_memory(
    request: ConversationMemoryCreate,
    db: Session = Depends(get_db)
):

    service = ConversationMemoryService(
        ConversationMemoryRepository(db)
    )

    return service.create(
        request.conversation_id
    )


@router.get(
    "/conversation/{conversation_id}",
    response_model=ConversationMemoryResponse
)
def get_conversation_memory(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    service = ConversationMemoryService(
        ConversationMemoryRepository(db)
    )

    return service.get_by_conversation_id(
        conversation_id
    )
