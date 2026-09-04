from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class MemoryItemResponse(BaseModel):

    id: int

    user_id: int

    type: str

    key: str

    content: str

    importance: float

    confidence: float

    freshness: float

    source_type: str

    source_conversation_id: Optional[int] = None

    source_chat_history_id: Optional[int] = None

    last_confirmed_at: Optional[datetime] = None

    scope: str

    status: str

    first_seen_at: datetime


    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True
