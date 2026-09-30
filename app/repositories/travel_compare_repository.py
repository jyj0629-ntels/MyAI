from app.models.travel_compare_history import TravelCompareHistory
from app.models.travel_round_response import TravelRoundResponse


class TravelCompareRepository:
    """DB access for the 2-round travel comparison feature."""

    def __init__(self, db):
        self.db = db

    def create_history(self, user_id, user_prompt, llm_model_used, status="PROCESSING"):
        history = TravelCompareHistory(
            user_id=user_id,
            user_prompt=user_prompt,
            llm_model_used=llm_model_used,
            status=status,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def add_round_response(self, history_id, round_no, ai_provider, raw_response, summary, status):
        row = TravelRoundResponse(
            history_id=history_id,
            round_no=round_no,
            ai_provider=ai_provider,
            raw_response=raw_response,
            summary=summary,
            status=status,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def set_round2_prompt(self, history_id, round2_prompt):
        history = (
            self.db.query(TravelCompareHistory)
            .filter(TravelCompareHistory.id == history_id)
            .first()
        )
        if history is None:
            return None
        history.round2_prompt = round2_prompt
        self.db.commit()
        self.db.refresh(history)
        return history

    def update_result(self, history_id, final_result, status):
        history = (
            self.db.query(TravelCompareHistory)
            .filter(TravelCompareHistory.id == history_id)
            .first()
        )
        if history is None:
            return None
        history.final_result = final_result
        history.status = status
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_history_list(self, limit=30):
        return (
            self.db.query(TravelCompareHistory)
            .order_by(TravelCompareHistory.id.desc())
            .limit(limit)
            .all()
        )

    def get_history(self, history_id):
        return (
            self.db.query(TravelCompareHistory)
            .filter(TravelCompareHistory.id == history_id)
            .first()
        )

    def get_round_responses(self, history_id):
        return (
            self.db.query(TravelRoundResponse)
            .filter(TravelRoundResponse.history_id == history_id)
            .order_by(TravelRoundResponse.round_no.asc(), TravelRoundResponse.id.asc())
            .all()
        )
