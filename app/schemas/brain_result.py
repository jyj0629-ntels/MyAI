from pydantic import BaseModel


class BrainResult(BaseModel):

    task_type: str

    role: str

    provider: str

    reason: str

    prompt: str
