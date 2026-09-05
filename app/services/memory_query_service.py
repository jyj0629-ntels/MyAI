import re
from difflib import SequenceMatcher

from app.services.memory_retrieval_engine import (
    MemoryRetrievalEngine
)


class MemoryQueryService:

    def __init__(
        self,
        memory_service
    ):
        self.memory_service = (
            memory_service
        )

        self.engine = (
            MemoryRetrievalEngine()
        )

    @staticmethod
    def _normalize_memory_text(value: str) -> str:
        text = (value or "").strip().lower()
        text = re.sub(r"[^0-9a-z가-힣\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @classmethod
    def deduplicate_memories(cls, memories: list):
        unique = []
        for memory in memories:
            content = getattr(memory, "content", str(memory)) or ""
            normalized = cls._normalize_memory_text(content)
            if not normalized:
                continue

            duplicate = False
            for existing in unique:
                existing_norm = cls._normalize_memory_text(getattr(existing, "content", str(existing)) or "")
                similarity = SequenceMatcher(None, normalized, existing_norm).ratio()
                if similarity >= 0.82:
                    duplicate = True
                    break

            if not duplicate:
                unique.append(memory)

        return unique

    def query(
        self,
        user_id: int,
        question: str
    ):

        preferences = (
            self.memory_service.get_by_type(
                user_id,
                "PREFERENCE"
            )
        )

        goals = (
            self.memory_service.get_by_type(
                user_id,
                "GOAL"
            )
        )

        projects = (
            self.memory_service.get_by_type(
                user_id,
                "PROJECT"
            )
        )

        consolidated_preferences = (
            self.engine.consolidation_service
            .consolidate(
                preferences
            )
        )

        consolidated_goals = (
            self.engine.consolidation_service
            .consolidate(
                goals
            )
        )

        consolidated_projects = (
            self.engine.consolidation_service
            .consolidate(
                projects
            )
        )

        result = (
            self.deduplicate_memories(
                consolidated_preferences
                + consolidated_goals
                + consolidated_projects
            )
        )

        print()
        print("# --------------------------------")
        print("# MEMORY QUERY")
        print("# --------------------------------")
        print(
            f"user_id={user_id}"
        )
        print(
            f"question={question}"
        )
        print(
            f"preferences={len(consolidated_preferences)}"
        )
        print(
            f"goals={len(consolidated_goals)}"
        )
        print(
            f"projects={len(consolidated_projects)}"
        )
        print(
            f"total={len(result)}"
        )
        print("# --------------------------------")
        print()

        return result
