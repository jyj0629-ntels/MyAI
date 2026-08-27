from pydantic import BaseModel
from typing import Optional


class AIRequest(BaseModel):

    user_id: int | None = None

    question: str

    system_prompt: str = ""

    user_context: str = ""

    temperature: float = 0.2

    provider: Optional[str] = None

    conversation_id: Optional[int] = None

    prompt: Optional[str] = None
