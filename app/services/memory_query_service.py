import re
from difflib import SequenceMatcher

from app.services.memory_retrieval_engine import (
    MemoryRetrievalEngine
)


class MemoryQueryService:
    @staticmethod
    def detect_question_theme(question: str) -> str:
        text = (question or "").lower()
        purchase_keywords = [
            "구매", "구입", "상품", "제품", "브랜드", "가격", "예산", "가성비", "후기", "리뷰",
            "평점", "쇼핑", "비교", "추천", "top3", "선택", "토퍼", "의자", "노트북", "폰",
            "휴대폰", "가전", "세탁기", "에어컨", "tv", "모니터", "마우스", "키보드", "구매 링크"
        ]
        dev_keywords = [
            "개발", "코드", "프로그램", "프로그래밍", "api", "fastapi", "docker", "db", "sql",
            "설계", "리팩토링", "버그", "테스트", "백엔드", "앱", "플랫폼", "architecture",
            "system", "기술", "배포", "인프라", "디버그", "기능"
        ]

        purchase_score = sum(1 for keyword in purchase_keywords if keyword in text)
        dev_score = sum(1 for keyword in dev_keywords if keyword in text)

        if purchase_score > dev_score:
            return "purchase"
        if dev_score > purchase_score:
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
                if any(keyword in normalized for keyword in ["가성비", "후기", "리뷰", "가격", "구매", "추천", "제품", "상품", "예산", "비교", "top3", "브랜드", "토퍼", "의자", "노트북", "휴대폰", "모니터", "구매 링크"]):
                    relevant.append(memory)
                elif not any(keyword in normalized for keyword in ["개발", "코드", "api", "fastapi", "docker", "디버그", "설계", "리팩토링", "테스트", "백엔드"]):
                    relevant.append(memory)
                continue

            if theme == "development":
                if any(keyword in normalized for keyword in ["개발", "코드", "api", "fastapi", "docker", "db", "sql", "디버그", "설계", "리팩토링", "테스트", "백엔드", "아키텍처", "시스템", "프로그램"]):
                    relevant.append(memory)
                elif not any(keyword in normalized for keyword in ["가성비", "후기", "가격", "구매", "상품", "제품", "예산", "토퍼", "의자", "브랜드", "쇼핑"]):
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
