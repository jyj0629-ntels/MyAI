from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ForbiddenTermCreate(BaseModel):
    term: str
    term_type: str = "WORD"  # WORD | SENTENCE
    replacement_hint: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class ForbiddenTermUpdate(BaseModel):
    term: Optional[str] = None
    term_type: Optional[str] = None
    replacement_hint: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ForbiddenTermResponse(BaseModel):
    id: int
    term: str
    term_type: str
    replacement_hint: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
