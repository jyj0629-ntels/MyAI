from sqlalchemy import text

from app.db.database import SessionLocal


class MemoryRepository:

    def get_memories(self, user_id: int):

        db = SessionLocal()

        try:

            result = db.execute(
                text(
                    """
                    SELECT
                        memory_type,
                        memory_key,
                        memory_value,
                        confidence,
                        status
                    FROM personal_memory
                    WHERE user_id = :user_id
                      AND status = 'CONFIRMED'
                    ORDER BY confidence DESC
                    """
                ),
                {
                    "user_id": user_id
                }
            )

            return [
                {
                    "memory_type": row.memory_type,
                    "memory_key": row.memory_key,
                    "memory_value": row.memory_value,
                    "confidence": float(row.confidence or 0),
                    "status": row.status
                }
                for row in result
            ]

        finally:

            db.close()
