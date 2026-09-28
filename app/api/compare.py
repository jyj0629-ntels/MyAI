from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.repositories.compare_repository import CompareRepository
from app.services.compare_service import CompareService
from app.services.compare_scraper_service import SUPPORTED_PROVIDERS

router = APIRouter(prefix="/compare", tags=["compare"])


class CompareRunRequest(BaseModel):
    question: str
    providers: list[str] | None = None
    llm_model: str | None = None
    user_id: int | None = 1


def _service(db: Session) -> CompareService:
    return CompareService(CompareRepository(db))


@router.post("/run")
async def run_compare(
    payload: CompareRunRequest = Body(...),
    db: Session = Depends(get_db),
):
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=422, detail="question is required and must be non-empty.")

    providers = payload.providers or list(SUPPORTED_PROVIDERS)
    providers = [p.strip().lower() for p in providers if p and p.strip()]
    providers = [p for p in providers if p in SUPPORTED_PROVIDERS]
    if not providers:
        raise HTTPException(
            status_code=422,
            detail=f"providers must include at least one of {list(SUPPORTED_PROVIDERS)}.",
        )

    result = await _service(db).run(
        user_id=payload.user_id,
        user_prompt=question,
        providers=providers,
        llm_model_used=payload.llm_model,
    )
    return result


@router.get("/history")
def compare_history(limit: int = 30, db: Session = Depends(get_db)):
    return _service(db).get_history_list(limit)


@router.get("/history/{history_id}")
def compare_history_detail(history_id: int, db: Session = Depends(get_db)):
    detail = _service(db).get_detail(history_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="compare history not found.")
    return detail
