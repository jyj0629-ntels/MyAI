from fastapi import APIRouter
from fastapi import Depends

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

from app.repositories.chat_repository import ChatRepository
from app.services.chat_service import ChatService

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
