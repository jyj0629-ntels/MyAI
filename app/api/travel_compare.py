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
    country: str
    region: str
    period: str = ""
    must_see: str = ""
    period_notes: str = ""
    remarks: str = ""
    providers: list[str] | None = None
    llm_model: str | None = None
    user_id: int | None = 1


@router.post("/run")
async def run_travel_compare(
    payload: TravelRunRequest = Body(...),
    db: Session = Depends(get_db),
):
    if not (payload.country or "").strip() or not (payload.region or "").strip():
        raise HTTPException(status_code=422, detail="country and region are required.")

    allowed = _public_providers()
    providers = payload.providers or allowed
    providers = [p.strip().lower() for p in providers if p and p.strip()]
    providers = [p for p in providers if p in allowed]
    if not providers:
        raise HTTPException(
            status_code=422,
            detail=f"providers must include at least one of {allowed}.",
        )

    form = {
        "country": payload.country.strip(),
        "region": payload.region.strip(),
        "period": (payload.period or "").strip(),
        "must_see": (payload.must_see or "").strip(),
        "period_notes": (payload.period_notes or "").strip(),
        "remarks": (payload.remarks or "").strip(),
    }

    result = await TravelCompareService(db).run(
        user_id=payload.user_id,
        form=form,
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
