import json
from typing import Any, Optional

from pydantic import BaseModel, field_validator


class AIRequest(BaseModel):

    user_id: Optional[int] = None

    question: str = ""

    system_prompt: str = ""

    user_context: str = ""

    temperature: float = 0.2

    provider: Optional[str] = None

    selected_providers: Optional[list[str]] = None

    conversation_id: Optional[int] = None

    prompt: Optional[str] = None

    response_format_template_id: Optional[int] = None

    response_format_text: Optional[str] = None

    think: bool = False

    @field_validator("question", mode="before")
    @classmethod
    def normalize_question(cls, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        value = str(value).strip()
        return value

    @classmethod
    def from_payload(cls, payload: Any) -> "AIRequest":
        if payload is None:
            payload = {}

        if isinstance(payload, cls):
            return payload

        if hasattr(payload, "model_dump"):
            payload = payload.model_dump()

        if not isinstance(payload, dict):
            raise ValueError("Request payload must be a JSON object.")

        normalized = dict(payload)

        if "question" not in normalized or not str(normalized.get("question") or "").strip():
            for key in ("prompt", "query", "message", "input", "text"):
                candidate = normalized.get(key)
                if candidate is not None and str(candidate).strip():
                    normalized["question"] = candidate
                    break

        if "question" not in normalized or not str(normalized.get("question") or "").strip():
            raise ValueError("question is required and must be a non-empty string.")

        if "user_id" in normalized and normalized["user_id"] not in (None, ""):
            try:
                normalized["user_id"] = int(normalized["user_id"])
            except (TypeError, ValueError):
                normalized["user_id"] = None

        if "conversation_id" in normalized and normalized["conversation_id"] not in (None, ""):
            try:
                normalized["conversation_id"] = int(normalized["conversation_id"])
            except (TypeError, ValueError):
                normalized["conversation_id"] = None

        if "selected_providers" in normalized and normalized["selected_providers"] not in (None, ""):
            providers = normalized["selected_providers"]
            if isinstance(providers, str):
                providers = [item.strip() for item in providers.split(",") if item.strip()]
            normalized["selected_providers"] = [
                str(item).strip().lower() for item in providers if str(item).strip()
            ]

        return cls(**normalized)
