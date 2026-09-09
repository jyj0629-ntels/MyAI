import re

from app.models.memory_item import MemoryItem
from app.models.user import User


class PreferenceExtractionService:
    """Extract durable preferences from a user question without brittle string matching."""

    @staticmethod
    def normalize_text(value: str) -> str:
        text = (value or "").strip()
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def should_register_preference(frequency: int, threshold: int | None = None, theme: str | None = None) -> bool:
        minimum = int(
            threshold
            if threshold is not None
            else getattr(__import__("app.core.config", fromlist=["settings"]).settings, "PREFERENCE_MIN_FREQUENCY", 2)
        )
        return int(frequency or 0) >= minimum

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token for token in re.findall(r"[가-힣A-Za-z0-9]+", (text or "").lower()) if len(token) > 1]

    @classmethod
    def _score_preferences(cls, text: str) -> dict[str, float]:
        tokens = set(cls._tokenize(text))
        score_map = {
            "value": {"가성비", "가격", "예산", "합리", "저렴", "경제", "비용"},
            "reviews": {"리뷰", "평점", "후기", "평판", "추천", "검증", "비교"},
            "format": {"표", "정리", "요약", "한눈", "간단", "리스트", "비교"},
            "shopping": {"구매", "상품", "제품", "브랜드", "쇼핑", "선택", "추천"},
        }
        scores = {name: 0.0 for name in score_map}
        for name, keywords in score_map.items():
            overlap = len(tokens & {keyword.lower() for keyword in keywords})
            scores[name] = float(overlap)
        return scores

    @classmethod
    def extract(cls, question: str):
        text = cls.normalize_text(question)
        preferences = []

        if not text:
            return preferences

        scores = cls._score_preferences(text)
        dominant = max(scores.items(), key=lambda item: item[1], default=("shopping", 0.0))[0]

        if scores["value"] > 0:
            preferences.append({
                "type": "PREFERENCE",
                "key": "purchase_pref_value",
                "content": "사용자는 가격 대비 만족도가 높은 옵션을 선호한다.",
                "importance": 0.9,
                "confidence": min(0.95, 0.6 + (scores["value"] * 0.1)),
            })

        if scores["reviews"] > 0:
            preferences.append({
                "type": "PREFERENCE",
                "key": "purchase_pref_reviews",
                "content": "사용자는 후기와 검증된 평판이 있는 선택지를 우선적으로 선호한다.",
                "importance": 0.85,
                "confidence": min(0.95, 0.6 + (scores["reviews"] * 0.1)),
            })

        if scores["format"] > 0:
            preferences.append({
                "type": "PREFERENCE",
                "key": "purchase_pref_format",
                "content": "사용자는 비교를 한눈에 볼 수 있도록 표나 정리된 형식을 선호한다.",
                "importance": 0.8,
                "confidence": min(0.95, 0.6 + (scores["format"] * 0.1)),
            })

        if dominant == "shopping" or scores["shopping"] > 0:
            preferences.append({
                "type": "PREFERENCE",
                "key": "purchase_pref_shopping",
                "content": "사용자는 실용적이고 합리적인 상품 선택을 선호한다.",
                "importance": 0.75,
                "confidence": min(0.95, 0.6 + (scores["shopping"] * 0.1)),
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

    @staticmethod
    def ensure_user_exists(user_id: int, db):
        if not user_id:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if user is not None:
            return user

        base_email = f"demo_user_{user_id}@local.invalid"
        email = base_email
        suffix = 1
        while db.query(User).filter(User.email == email).first() is not None:
            email = f"demo_user_{user_id}_{suffix}@local.invalid"
            suffix += 1

        user = User(email=email, name=f"Demo User {user_id}")
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def persist_from_question(cls, user_id: int, question: str, db):
        if not user_id or not question:
            return []

        cls.ensure_user_exists(user_id, db)

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

            frequency = 1
            if existing is not None:
                frequency = int(getattr(existing, "freshness", 0) or 0) + 1 if hasattr(existing, "freshness") else int(getattr(existing, "confidence", 0) or 0) + 1
                existing.freshness = float(frequency)
                existing.confidence = min(0.99, float(existing.confidence or 0.5) + 0.05)
                if cls.should_register_preference(frequency, getattr(__import__("app.core.config", fromlist=["settings"]).settings, "PREFERENCE_MIN_FREQUENCY", 2)):
                    existing.status = "ACTIVE"
                    existing.importance = max(float(existing.importance or 0.5), 0.8)
                db.add(existing)
                continue

            if cls.should_register_preference(frequency, getattr(__import__("app.core.config", fromlist=["settings"]).settings, "PREFERENCE_MIN_FREQUENCY", 2)):
                status = "ACTIVE"
            else:
                status = "CANDIDATE"

            memory = MemoryItem(
                user_id=user_id,
                type=item["type"],
                key=item["key"],
                content=item["content"],
                importance=item["importance"],
                confidence=item["confidence"],
                freshness=float(frequency),
                source_type="QUESTION",
                scope="USER",
                status=status,
            )
            db.add(memory)
            saved.append(memory)

        if saved:
            try:
                db.commit()
                for memory in saved:
                    db.refresh(memory)
            except Exception:
                db.rollback()
                raise

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return saved

    @staticmethod
    def build_frequency_threshold(theme: str | None = None) -> int:
        default_threshold = getattr(__import__("app.core.config", fromlist=["settings"]).settings, "PREFERENCE_MIN_FREQUENCY", 2)
        return int(default_threshold)
