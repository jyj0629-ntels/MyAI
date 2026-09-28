from app.models.compare_history import CompareHistory
from app.models.compare_source_response import CompareSourceResponse


class CompareRepository:
    """DB access for the /demo_compare feature (histories + per-provider source responses)."""

    def __init__(self, db):
        self.db = db

    def create_history(self, user_id, user_prompt, llm_model_used, status="PROCESSING"):
        history = CompareHistory(
            user_id=user_id,
            user_prompt=user_prompt,
            llm_model_used=llm_model_used,
            status=status,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def add_source_response(self, history_id, ai_provider, raw_response, status):
        source = CompareSourceResponse(
            history_id=history_id,
            ai_provider=ai_provider,
            raw_response=raw_response,
            status=status,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def update_history_result(self, history_id, summary_result, status):
        history = (
            self.db.query(CompareHistory)
            .filter(CompareHistory.id == history_id)
            .first()
        )
        if history is None:
            return None
        history.summary_result = summary_result
        history.status = status
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_history_list(self, limit=30):
        return (
            self.db.query(CompareHistory)
            .order_by(CompareHistory.id.desc())
            .limit(limit)
            .all()
        )

    def get_history(self, history_id):
        return (
            self.db.query(CompareHistory)
            .filter(CompareHistory.id == history_id)
            .first()
        )

    def get_source_responses(self, history_id):
        return (
            self.db.query(CompareSourceResponse)
            .filter(CompareSourceResponse.history_id == history_id)
            .order_by(CompareSourceResponse.id.asc())
            .all()
        )
