from app.services.memory_policy_service import \
    MemoryPolicyService


service = (
    MemoryPolicyService()
)

print(
    service.should_always_include(
        "PREFERENCE"
    )
)

print(
    service.should_always_include(
        "GOAL"
    )
)

print(
    service.should_relevance_search(
        "PROJECT"
    )
)

print(
    service.should_relevance_search(
        "KNOWLEDGE"
    )
)
