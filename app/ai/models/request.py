from pydantic import BaseModel
from typing import Optional


class AIRequest(BaseModel):

    question: str

    system_prompt: str = ""

    user_context: str = ""

    temperature: float = 0.2

    provider: Optional[str] = None
