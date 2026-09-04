from pydantic import BaseModel
from typing import Optional


class MemoryItemCreate(BaseModel):

    user_id: int

    type: str

    key: str

    content: str

    importance: float = 0.5

    confidence: float = 0.5

    freshness: float = 1.0

    source_type: str = "MANUAL"

    source_conversation_id: Optional[int] = None
    
    source_chat_history_id: Optional[int] = None

    scope: str = "USER"

    status: str = "ACTIVE"
