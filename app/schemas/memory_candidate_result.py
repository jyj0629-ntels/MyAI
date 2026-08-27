from pydantic import BaseModel

from app.schemas.memory_candidate import \
    MemoryCandidate


class MemoryCandidateResult(
    BaseModel
):
    memories: list[
        MemoryCandidate
    ]
