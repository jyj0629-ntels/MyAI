from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ChatHistoryResponse(BaseModel):

    id: int
    provider: str
    model: str

    question: str
    answer: str

    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    success: bool

    created_at: datetime

    class Config:
        from_attributes = True
