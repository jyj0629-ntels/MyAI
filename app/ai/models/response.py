from pydantic import BaseModel
from typing import Any, Optional


class AIResponse(BaseModel):
    provider: str

    model: Optional[str] = None

    answer: str

    summary: Optional[str] = None

    comparison: Optional[dict[str, Any]] = None

    sources: Optional[list[dict[str, Any]]] = None

    input_tokens: Optional[int] = None

    output_tokens: Optional[int] = None

    success: bool = True

    error: Optional[str] = None

    performance: Optional[dict[str, Any]] = None

    requires_confirmation: bool = False
