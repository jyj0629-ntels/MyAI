from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.repositories.memory_item_repository import \
    MemoryItemRepository

from app.services.memory_item_service import \
    MemoryItemService

from app.schemas.memory_item import \
    MemoryItemResponse

from app.schemas.memory_item_create import \
    MemoryItemCreate

from app.models.memory_item import MemoryItem


router = APIRouter(
    prefix="/memory-items",
    tags=["memory-items"]
)


@router.post(
    "/",
    response_model=MemoryItemResponse
)
def create_memory_item(
    request: MemoryItemCreate,
    db: Session = Depends(get_db)
):

    service = MemoryItemService(
        MemoryItemRepository(db)
    )

    memory_item = MemoryItem(
        user_id=request.user_id,
        type=request.type,
        key=request.key,
        content=request.content,
        importance=request.importance,
        confidence=request.confidence,
        freshness=request.freshness,
        source_type=request.source_type,
        source_conversation_id=request.source_conversation_id,
        source_chat_history_id=request.source_chat_history_id,
        scope=request.scope,
        status=request.status
    )

    return service.create(
        memory_item
    )

@router.get(
    "/user/{user_id}",
    response_model=list[MemoryItemResponse]
)
def get_user_memories(
    user_id: int,
    db: Session = Depends(get_db)
):

    service = MemoryItemService(
        MemoryItemRepository(db)
    )

    return service.get_by_user(
        user_id
    )


@router.get(
    "/user/{user_id}/active",
    response_model=list[MemoryItemResponse]
)
def get_active_memories(
    user_id: int,
    db: Session = Depends(get_db)
):

    service = MemoryItemService(
        MemoryItemRepository(db)
    )

    return service.get_active_memories(
        user_id
    )
