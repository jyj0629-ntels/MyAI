class MemoryPolicyService:

    def should_always_include(
        self,
        memory_type: str
    ):

        return memory_type in [
            "PREFERENCE",
            "GOAL"
        ]

    def should_relevance_search(
        self,
        memory_type: str
    ):

        return memory_type in [
            "PROJECT",
            "KNOWLEDGE"
        ]
