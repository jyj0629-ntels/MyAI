from app.models.response_format_template import ResponseFormatTemplate
from app.repositories.response_format_template_repository import ResponseFormatTemplateRepository
from app.schemas.response_format_template_create import ResponseFormatTemplateCreate


class ResponseFormatTemplateService:
    def __init__(self, repository: ResponseFormatTemplateRepository):
        self.repository = repository

    def create(self, payload: ResponseFormatTemplateCreate):
        template = ResponseFormatTemplate(
            user_id=payload.user_id,
            name=payload.name,
            description=payload.description,
            template_text=payload.template_text,
            is_default=payload.is_default,
            is_active=payload.is_active,
        )
        return self.repository.create(template)

    def get_by_id(self, template_id: int):
        return self.repository.get_by_id(template_id)

    def list_for_user(self, user_id: int | None = None):
        return self.repository.get_by_user(user_id)

    def get_default(self, user_id: int | None = None):
        return self.repository.get_default(user_id)

    def update(self, template_id: int, payload: ResponseFormatTemplateCreate):
        template = self.repository.get_by_id(template_id)
        if not template:
            return None
        template.user_id = payload.user_id
        template.name = payload.name
        template.description = payload.description
        template.template_text = payload.template_text
        template.is_default = payload.is_default
        template.is_active = payload.is_active
        return self.repository.update(template)

    def delete(self, template_id: int):
        template = self.repository.get_by_id(template_id)
        if not template:
            return None
        return self.repository.delete(template)
