from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ChatHistoryResponse(BaseModel):

    id: int
    feature: str = "myai"
    provider: str
    model: str

    question: str
    answer: str
    provider_response_path: Optional[str] = None
    generated_prompt: Optional[str] = None
    provider_responses_json: Optional[str] = None

    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    success: bool

    created_at: datetime

    class Config:
        from_attributes = True
