from datetime import datetime

from pydantic import BaseModel


class ChatHistoryResponse(BaseModel):

    id: int
    provider: str
    model: str

    question: str
    answer: str

    input_tokens: int | None = None
    output_tokens: int | None = None

    success: bool

    created_at: datetime

    class Config:
        from_attributes = True
