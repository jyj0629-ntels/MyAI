from datetime import datetime

from pydantic import BaseModel


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

    source_conversation_id: int | None = None

    source_chat_history_id: int | None = None

    scope: str

    status: str

    first_seen_at: datetime

    last_confirmed_at: datetime | None = None

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True
