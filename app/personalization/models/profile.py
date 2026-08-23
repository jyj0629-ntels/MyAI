from pydantic import BaseModel
from typing import List, Dict


class PersonalProfile(BaseModel):

    user_id: int

    preferred_answer_style: str = ""

    interests: List[str] = []

    preferences: Dict[str, str] = {}

    decision_style: str = ""

    important_constraints: List[str] = []
