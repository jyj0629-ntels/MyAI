from __future__ import annotations

from typing import Any


class ProviderSelectorService:
    """Choose the preferred public AI providers based on the question theme."""

    def __init__(self):
        self.provider_map = {
            "finance": ["gemini", "openai", "groq"],
            "shopping": ["gemini", "openai", "copilot"],
            "schedule": ["gemini", "copilot", "openai"],
            "travel": ["gemini", "openai"],
            "work": ["openai", "gemini", "copilot"],
            "personal": ["gemini", "copilot", "openai"],
            "general": ["gemini", "openai", "copilot"],
        }

    def select(self, question_theme: str, user_profile: dict[str, Any] | None = None) -> list[str]:
        theme = (question_theme or "general").lower()
        providers = list(self.provider_map.get(theme, self.provider_map["general"]))

        if user_profile and user_profile.get("preferences"):
            preferred = user_profile.get("preferences", {}).get("preferred_provider")
            if preferred and preferred in providers:
                providers = [preferred] + [item for item in providers if item != preferred]

        return providers
