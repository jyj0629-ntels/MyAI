from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.forbidden_term import ForbiddenTerm
from app.repositories.forbidden_term_repository import ForbiddenTermRepository

from app.schemas.forbidden_term import (
    ForbiddenTermCreate,
    ForbiddenTermResponse,
    ForbiddenTermUpdate,
)

router = APIRouter(
    prefix="/forbidden-terms",
    tags=["forbidden-terms"],
)


@router.get("/", response_model=list[ForbiddenTermResponse])
def list_forbidden_terms(
    include_inactive: bool = True,
    db: Session = Depends(get_db),
):
    repo = ForbiddenTermRepository(db)
    return repo.get_all(include_inactive=include_inactive)


@router.post("/", response_model=ForbiddenTermResponse)
def create_forbidden_term(
    payload: ForbiddenTermCreate,
    db: Session = Depends(get_db),
):
    term = (payload.term or "").strip()
    if not term:
        raise HTTPException(status_code=422, detail="term is required and must be non-empty.")

    repo = ForbiddenTermRepository(db)

    if repo.exists_by_term(term):
        raise HTTPException(status_code=409, detail="이미 등록된 금지어입니다.")

    entity = ForbiddenTerm(
        term=term,
        term_type=(payload.term_type or "WORD").strip().upper(),
        replacement_hint=payload.replacement_hint,
        category=payload.category,
        description=payload.description,
        is_active=payload.is_active,
    )

    return repo.create(entity)


@router.put("/{term_id}", response_model=ForbiddenTermResponse)
def update_forbidden_term(
    term_id: int,
    payload: ForbiddenTermUpdate,
    db: Session = Depends(get_db),
):
    repo = ForbiddenTermRepository(db)
    entity = repo.get_by_id(term_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="forbidden term not found")

    if payload.term is not None:
        entity.term = payload.term.strip()
    if payload.term_type is not None:
        entity.term_type = payload.term_type.strip().upper()
    if payload.replacement_hint is not None:
        entity.replacement_hint = payload.replacement_hint
    if payload.category is not None:
        entity.category = payload.category
    if payload.description is not None:
        entity.description = payload.description
    if payload.is_active is not None:
        entity.is_active = payload.is_active

    return repo.update(entity)


@router.delete("/{term_id}")
def delete_forbidden_term(
    term_id: int,
    db: Session = Depends(get_db),
):
    repo = ForbiddenTermRepository(db)
    entity = repo.get_by_id(term_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="forbidden term not found")

    repo.delete(entity)
    return {"deleted": True, "id": term_id}
