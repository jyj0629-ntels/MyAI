import re

from app.models.memory_item import MemoryItem


class PreferenceExtractionService:
    """Extract durable preferences from a user purchase question."""

    @staticmethod
    def normalize_text(value: str) -> str:
        text = (value or "").strip()
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _matches_any(text: str, keywords: list[str]) -> bool:
        lowered = text.lower()
        return any(keyword.lower() in lowered for keyword in keywords)

    @classmethod
    def extract(cls, question: str):
        text = cls.normalize_text(question)
        preferences = []

        if not text:
            return preferences

        pattern_map = [
            (
                "가성비",
                ["가성비", "value for money", "가성", "합리적 가격", "가격 대비"],
                "사용자는 구매 시 가성비가 좋은 제품을 선호한다."
            ),
            (
                "평가수",
                ["제품평", "리뷰", "평점", "후기", "많은 제품평", "인터넷 리뷰"],
                "사용자는 제품 후기와 평판이 좋은 상품을 우선적으로 선호한다."
            ),
            (
                "top3",
                ["top3", "상위 3", "3개", "top 3", "top3 제품", "비교표", "표로"],
                "사용자는 비교를 위해 Top3 또는 핵심 후보 3개를 한눈에 볼 수 있는 형식으로 정보를 선호한다."
            ),
            (
                "간결표현",
                ["표", "테이블", "표로", "한눈에", "간결", "정리"],
                "사용자는 구매 비교를 표 형식으로 간결하게 한눈에 보는 것을 선호한다."
            ),
            (
                "구매링크",
                ["구매 링크", "링크", "구매하기", "구매 링크 포함", "쇼핑 링크"],
                "사용자는 제품 선택 시 구매 링크와 바로가기 정보를 함께 보길 원한다."
            ),
            (
                "가격대",
                ["10만원대", "10만원", "예산", "가격대", "범위"],
                "사용자는 예산 범위 내에서 제품을 선택하는 것을 선호한다."
            ),
        ]

        for key, keywords, content in pattern_map:
            if cls._matches_any(text, keywords):
                preferences.append({
                    "type": "PREFERENCE",
                    "key": f"purchase_pref_{key.lower()}",
                    "content": content,
                    "importance": 0.9,
                    "confidence": 0.9,
                })

        if not preferences:
            preferences.append({
                "type": "PREFERENCE",
                "key": "purchase_pref_general",
                "content": "사용자는 합리적인 가격과 비교 정보가 포함된 제품 추천을 선호한다.",
                "importance": 0.8,
                "confidence": 0.8,
            })

        unique = []
        seen = set()
        for item in preferences:
            if item["key"] in seen:
                continue
            seen.add(item["key"])
            unique.append(item)
        return unique

    @classmethod
    def persist_from_question(cls, user_id: int, question: str, db):
        if not user_id or not question:
            return []

        memories = cls.extract(question)
        saved = []

        for item in memories:
            existing = (
                db.query(MemoryItem)
                .filter(
                    MemoryItem.user_id == user_id,
                    MemoryItem.key == item["key"]
                )
                .first()
            )
            if existing:
                continue

            memory = MemoryItem(
                user_id=user_id,
                type=item["type"],
                key=item["key"],
                content=item["content"],
                importance=item["importance"],
                confidence=item["confidence"],
                freshness=1.0,
                source_type="QUESTION",
                scope="USER",
                status="ACTIVE",
            )
            db.add(memory)
            saved.append(memory)

        if saved:
            db.commit()
            for memory in saved:
                db.refresh(memory)

        return saved
