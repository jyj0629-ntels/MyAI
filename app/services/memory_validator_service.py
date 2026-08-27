from app.memory_constants import \
    MEMORY_STATUS_ACTIVE

from app.memory_constants import \
    MEMORY_STATUS_VALIDATED


class MemoryValidatorService:

    def validate(
        self,
        memory_item
    ):

        if memory_item.confidence >= 0.8:
            memory_item.status = (
                MEMORY_STATUS_VALIDATED
            )
        else:
            memory_item.status = (
                MEMORY_STATUS_ACTIVE
            )

        return memory_item
