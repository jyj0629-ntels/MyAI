from pydantic import BaseModel
from typing import Optional


class ResponseFormatTemplateCreate(BaseModel):
    user_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    template_text: str
    is_default: bool = False
    is_active: bool = True
