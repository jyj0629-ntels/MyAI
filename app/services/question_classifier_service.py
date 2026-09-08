from __future__ import annotations

from typing import Any


class QuestionClassifierService:
    """Classify a user question at a high level without any hardcoded domain mapping."""

    def classify(self, question: str) -> dict[str, Any]:
        text = (question or "").strip()
        if not text:
            return {
                "theme": "general",
                "intent": "ask",
                "urgency": "normal",
                "complexity": "medium",
            }

        words = text.split()
        lower = text.lower()

        urgency = "normal"
        if len(text) > 400 or any(token in lower for token in ("지금", "오늘", "즉시", "급함", "빨리")):
            urgency = "high"

        complexity = "medium"
        if len(words) > 25 or "?" in lower or len(text) > 250:
            complexity = "high"

        intent = "ask"
        if len(words) >= 8 or "?" in lower:
            intent = "research"

        return {
            "theme": "general",
            "intent": intent,
            "urgency": urgency,
            "complexity": complexity,
        }
