from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.response_format_template import ResponseFormatTemplate
from app.repositories.response_format_template_repository import ResponseFormatTemplateRepository
from app.schemas.response_format_template import ResponseFormatTemplateResponse
from app.schemas.response_format_template_create import ResponseFormatTemplateCreate
from app.services.response_format_template_service import ResponseFormatTemplateService

router = APIRouter(prefix="/response-format-templates", tags=["response-format-templates"])


@router.get("/", response_model=list[ResponseFormatTemplateResponse])
def list_templates(user_id: int | None = None, db: Session = Depends(get_db)):
    service = ResponseFormatTemplateService(ResponseFormatTemplateRepository(db))
    return service.list_for_user(user_id)


@router.get("/{template_id}", response_model=ResponseFormatTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    service = ResponseFormatTemplateService(ResponseFormatTemplateRepository(db))
    template = service.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="template not found")
    return template


@router.post("/", response_model=ResponseFormatTemplateResponse)
def create_template(request: ResponseFormatTemplateCreate, db: Session = Depends(get_db)):
    service = ResponseFormatTemplateService(ResponseFormatTemplateRepository(db))
    return service.create(request)


@router.put("/{template_id}", response_model=ResponseFormatTemplateResponse)
def update_template(template_id: int, request: ResponseFormatTemplateCreate, db: Session = Depends(get_db)):
    service = ResponseFormatTemplateService(ResponseFormatTemplateRepository(db))
    template = service.update(template_id, request)
    if not template:
        raise HTTPException(status_code=404, detail="template not found")
    return template


@router.delete("/{template_id}", response_model=ResponseFormatTemplateResponse)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    service = ResponseFormatTemplateService(ResponseFormatTemplateRepository(db))
    template = service.delete(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="template not found")
    return template
