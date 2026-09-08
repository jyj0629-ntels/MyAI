import re

from app.core.config import settings
from app.models.memory_item import MemoryItem
from app.models.user import User


class PreferenceExtractionService:
    """Extract durable user preferences without binding to any specific domain or product type."""

    @staticmethod
    def normalize_text(value: str) -> str:
        text = (value or "").strip()
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text

    @classmethod
    def extract(cls, question: str):
        text = cls.normalize_text(question)
        if not text:
            return []

        return [{
            "type": "PREFERENCE",
            "key": "user_preference_general",
            "content": "사용자는 현재 질문의 맥락에 맞는 구체적이고 실용적이며 바로 실행 가능한 답변을 선호한다.",
            "importance": 0.8,
            "confidence": 0.8,
        }]

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

            if existing:
                existing.occurrence_count = (existing.occurrence_count or 1) + 1
                if (
                    existing.status != "ACTIVE"
                    and existing.occurrence_count >= settings.PREFERENCE_MIN_FREQUENCY
                ):
                    existing.status = "ACTIVE"
                saved.append(existing)
                continue

            initial_status = "ACTIVE" if settings.PREFERENCE_MIN_FREQUENCY <= 1 else "CANDIDATE"

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
                status=initial_status,
                occurrence_count=1,
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

        return saved
