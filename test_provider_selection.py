from app.services.provider_selection_service import \
    ProviderSelectionService


service = (
    ProviderSelectionService()
)

print(
    service.select(
        "Redis 설계 검토"
    )
)
