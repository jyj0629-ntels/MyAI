from __future__ import annotations

from typing import Any


class PersonalProfileService:
    """Build and maintain a lightweight personal profile summary.

    This service does not replace the database model layer. Instead, it provides
    a simple, readable summary object that can be reused by personalization and
    prompt generation code.
    """

    def __init__(self):
        self.default_profile = {
            "personality_summary": "User profile has not been fully learned yet.",
            "interests": [],
            "preferences": {},
            "schedule_patterns": {},
            "question_themes": [],
            "confidence": 0.0,
        }

    def build_profile(self, memory_items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Create a profile summary from stored memory entries."""
        items = memory_items or []

        profile = dict(self.default_profile)
        preferences: dict[str, Any] = {}
        interests: list[str] = []

        for item in items:
            memory_type = str(item.get("memory_type", "")).upper()
            memory_key = str(item.get("memory_key", "")).strip()
            memory_value = str(item.get("memory_value", "")).strip()

            if not memory_key and not memory_value:
                continue

            if memory_type == "PREFERENCE":
                preferences[memory_key] = memory_value
            elif memory_type == "INTEREST":
                interests.append(memory_key)

        profile["preferences"] = preferences
        profile["interests"] = sorted(set(interests))

        if items:
            profile["confidence"] = min(1.0, 0.2 + (len(items) * 0.05))

        return profile
