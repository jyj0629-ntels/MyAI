from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):

    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True
