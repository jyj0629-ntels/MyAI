from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.dependencies import get_db
from app.services.travel_compare_service import TravelCompareService

router = APIRouter(prefix="/travel_compare", tags=["travel_compare"])


def _public_providers():
    return [p.strip().lower() for p in (settings.PUBLIC_PROVIDERS or "").split(",") if p.strip()]


class TravelRunRequest(BaseModel):
    question: str
    providers: list[str] | None = None
    llm_model: str | None = None
    user_id: int | None = 1


@router.post("/run")
async def run_travel_compare(
    payload: TravelRunRequest = Body(...),
    db: Session = Depends(get_db),
):
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=422, detail="question is required and must be non-empty.")

    allowed = _public_providers()
    providers = payload.providers or allowed
    providers = [p.strip().lower() for p in providers if p and p.strip()]
    providers = [p for p in providers if p in allowed]
    if not providers:
        raise HTTPException(
            status_code=422,
            detail=f"providers must include at least one of {allowed}.",
        )

    result = await TravelCompareService(db).run(
        user_id=payload.user_id,
        user_prompt=question,
        providers=providers,
        llm_model_used=payload.llm_model,
    )
    return result


@router.get("/history")
def travel_history(limit: int = 30, db: Session = Depends(get_db)):
    return TravelCompareService(db).get_history_list(limit)


@router.get("/history/{history_id}")
def travel_history_detail(history_id: int, db: Session = Depends(get_db)):
    detail = TravelCompareService(db).get_detail(history_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="travel compare history not found.")
    return detail
