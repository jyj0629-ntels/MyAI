from app.models.memory_item import MemoryItem

from app.services.memory_candidate_service import \
    MemoryCandidateService


memory = MemoryItem(
    user_id=3,
    type="PREFERENCE",
    key="answer_quality_priority",
    content="사용자는 정확도를 우선한다.",
    importance=0.95,
    confidence=0.92,
    freshness=1.0,
    source_type="LOCAL_LLM",
    scope="USER"
)

service = MemoryCandidateService()

candidate = service.create_candidate(
    memory
)

print(candidate.status)
