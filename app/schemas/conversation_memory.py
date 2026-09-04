from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ConversationMemoryCreate(BaseModel):

    conversation_id: int


class ConversationMemoryResponse(BaseModel):

    id: int

    conversation_id: int

    summary_md: Optional[str] = None

    current_goal: Optional[str] = None

    current_state: Optional[str] = None

    important_decisions: Optional[str] = None

    next_action: Optional[str] = None

    updated_at: datetime

    class Config:
        from_attributes = True
