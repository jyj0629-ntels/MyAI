from app.personalization.repositories.memory_repository import (
    MemoryRepository
)
from app.services.personal_profile_service import PersonalProfileService


class PersonalizationService:

    def __init__(self):

        self.memory_repository = MemoryRepository()
        self.profile_service = PersonalProfileService()

    def build_context(self, user_id: int) -> str:

        memories = self.memory_repository.get_memories(
            user_id
        )

        if not memories:
            return ""

        profile = self.profile_service.build_profile(memories)

        lines = []

        lines.append(
            "### USER PERSONAL CONTEXT"
        )
        lines.append(
            "### PERSONALITY SUMMARY"
        )
        lines.append(
            f"- {profile['personality_summary']}"
        )

        if profile.get("interests"):
            lines.append(
                "### INTEREST AREAS"
            )
            for interest in profile["interests"]:
                lines.append(f"- {interest}")

        if profile.get("preferences"):
            lines.append(
                "### USER PREFERENCES"
            )
            for key, value in profile["preferences"].items():
                lines.append(f"- {key}: {value}")

        lines.append(
            "### MEMORY FACTS"
        )

        for memory in memories:
            lines.append(
                f"- {memory['memory_key']}: "
                f"{memory['memory_value']}"
            )

        return "\n".join(lines)
