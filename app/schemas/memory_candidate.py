from pydantic import BaseModel


class MemoryCandidate(
    BaseModel
):
    type: str

    key: str

    content: str

    importance: float = 0.8

    confidence: float = 0.8
