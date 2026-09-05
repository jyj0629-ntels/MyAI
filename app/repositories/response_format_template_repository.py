from app.models.response_format_template import ResponseFormatTemplate


class ResponseFormatTemplateRepository:
    def __init__(self, db):
        self.db = db

    def create(self, template):
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_by_id(self, template_id: int):
        return self.db.query(ResponseFormatTemplate).filter(ResponseFormatTemplate.id == template_id).first()

    def get_by_user(self, user_id: int | None):
        query = self.db.query(ResponseFormatTemplate).filter(ResponseFormatTemplate.is_active == True)
        if user_id is not None:
            query = query.filter((ResponseFormatTemplate.user_id == user_id) | (ResponseFormatTemplate.user_id.is_(None)))
        else:
            query = query.filter(ResponseFormatTemplate.user_id.is_(None))
        return query.order_by(ResponseFormatTemplate.is_default.desc(), ResponseFormatTemplate.id.asc()).all()

    def get_default(self, user_id: int | None = None):
        query = self.db.query(ResponseFormatTemplate).filter(
            ResponseFormatTemplate.is_active == True,
            ResponseFormatTemplate.is_default == True
        )
        if user_id is not None:
            query = query.filter((ResponseFormatTemplate.user_id == user_id) | (ResponseFormatTemplate.user_id.is_(None)))
        else:
            query = query.filter(ResponseFormatTemplate.user_id.is_(None))
        return query.order_by(ResponseFormatTemplate.id.asc()).first()

    def list_all(self):
        return self.db.query(ResponseFormatTemplate).filter(ResponseFormatTemplate.is_active == True).order_by(ResponseFormatTemplate.id.asc()).all()

    def update(self, template):
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template):
        template.is_active = False
        self.db.commit()
        return template
