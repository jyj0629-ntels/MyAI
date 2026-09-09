import re
from difflib import SequenceMatcher

from app.core.config import settings
from app.services.memory_retrieval_engine import (
    MemoryRetrievalEngine
)


class MemoryQueryService:
    @staticmethod
    def detect_question_theme(question: str) -> str:
        from app.core.config import settings

        text = (question or "").strip()
        if not text:
            return "general"

        normalized = text.lower()
        purchase_keywords = [
            item.strip().lower() for item in (settings.PURCHASE_THEME_KEYWORDS or "").split(",") if item.strip()
        ]
        dev_keywords = [
            item.strip().lower() for item in (settings.DEVELOPMENT_THEME_KEYWORDS or "").split(",") if item.strip()
        ]

        purchase_score = sum(1 for keyword in purchase_keywords if keyword in normalized)
        dev_score = sum(1 for keyword in dev_keywords if keyword in normalized)

        if purchase_score and purchase_score >= dev_score:
            return "purchase"
        if dev_score and dev_score > purchase_score:
            return "development"

        if any(token in normalized for token in ("추천", "비교", "가격", "상품", "브랜드", "후기", "평점")):
            return "purchase"
        if any(token in normalized for token in ("코드", "api", "설계", "테스트", "백엔드", "db", "docker", "버그", "개발")):
            return "development"
        return "general"

    @classmethod
    def filter_relevant_memories(cls, memories, question: str):
        if not memories:
            return []

        theme = cls.detect_question_theme(question)
        relevant = []

        for memory in memories:
            content = str(getattr(memory, "content", memory) or "")
            normalized = content.lower()

            if theme == "purchase":
                purchase_keywords = [
                    item.strip().lower() for item in (settings.PURCHASE_THEME_KEYWORDS or "").split(",") if item.strip()
                ]
                if any(keyword in normalized for keyword in purchase_keywords):
                    relevant.append(memory)
                elif not any(keyword in normalized for keyword in ["개발", "코드", "api", "docker", "db", "sql", "설계", "테스트", "백엔드"]):
                    relevant.append(memory)
                continue

            if theme == "development":
                development_keywords = [
                    item.strip().lower() for item in (settings.DEVELOPMENT_THEME_KEYWORDS or "").split(",") if item.strip()
                ]
                if any(keyword in normalized for keyword in development_keywords):
                    relevant.append(memory)
                elif not any(keyword in normalized for keyword in ["구매", "상품", "제품", "가격", "예산", "가성비", "후기", "리뷰", "쇼핑"]):
                    relevant.append(memory)
                continue

            relevant.append(memory)

        return relevant

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

        result = self.deduplicate_memories(
            consolidated_preferences
            + consolidated_goals
            + consolidated_projects
        )
        result = self.filter_relevant_memories(result, question)

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
