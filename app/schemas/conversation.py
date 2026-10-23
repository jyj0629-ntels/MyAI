from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str
    feature: str = "myai"


class ConversationResponse(BaseModel):

    id: int
    title: str
    feature: str = "myai"
    created_at: datetime

    class Config:
        from_attributes = True
