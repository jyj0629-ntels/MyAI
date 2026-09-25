from app.models.forbidden_term import ForbiddenTerm


class ForbiddenTermRepository:

    def __init__(self, db):
        self.db = db

    def create(self, forbidden_term: ForbiddenTerm) -> ForbiddenTerm:
        self.db.add(forbidden_term)
        self.db.commit()
        self.db.refresh(forbidden_term)
        return forbidden_term

    def get_by_id(self, term_id: int) -> ForbiddenTerm | None:
        return (
            self.db.query(ForbiddenTerm)
            .filter(ForbiddenTerm.id == term_id)
            .first()
        )

    def get_all(self, include_inactive: bool = False):
        query = self.db.query(ForbiddenTerm)
        if not include_inactive:
            query = query.filter(ForbiddenTerm.is_active.is_(True))
        return query.order_by(ForbiddenTerm.id.asc()).all()

    def get_active(self):
        return (
            self.db.query(ForbiddenTerm)
            .filter(ForbiddenTerm.is_active.is_(True))
            .order_by(ForbiddenTerm.id.asc())
            .all()
        )

    def exists_by_term(self, term: str) -> bool:
        return (
            self.db.query(ForbiddenTerm)
            .filter(ForbiddenTerm.term == term)
            .first()
            is not None
        )

    def update(self, forbidden_term: ForbiddenTerm) -> ForbiddenTerm:
        self.db.commit()
        self.db.refresh(forbidden_term)
        return forbidden_term

    def delete(self, forbidden_term: ForbiddenTerm) -> None:
        self.db.delete(forbidden_term)
        self.db.commit()
