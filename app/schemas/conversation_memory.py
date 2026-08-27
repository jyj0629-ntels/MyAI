from datetime import datetime

from pydantic import BaseModel


class ConversationMemoryCreate(BaseModel):

    conversation_id: int


class ConversationMemoryResponse(BaseModel):

    id: int

    conversation_id: int

    summary_md: str | None = None

    current_goal: str | None = None

    current_state: str | None = None

    important_decisions: str | None = None

    next_action: str | None = None

    updated_at: datetime

    class Config:
        from_attributes = True
