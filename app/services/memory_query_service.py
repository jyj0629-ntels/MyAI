from app.services.memory_retrieval_engine import \
    MemoryRetrievalEngine


class MemoryQueryService:

    def __init__(
        self,
        memory_service
    ):
        self.memory_service = (
            memory_service
        )

        self.engine = (
            MemoryRetrievalEngine()
        )

    def query(
        self,
        user_id: int,
        question: str
    ):

        preferences = (
            self.memory_service.get_by_type(
                user_id,
                "PREFERENCE"
            )
        )

        goals = (
            self.memory_service.get_by_type(
                user_id,
                "GOAL"
            )
        )

        projects = (
            self.memory_service.get_by_type(
                user_id,
                "PROJECT"
            )
        )

        relevant_projects = (
            self.engine.retrieve(
                question=question,
                memories=projects
            )
        )

        consolidated_preferences = ( 
            self.engine.consolidation_service 
            .consolidate( 
                preferences
            )
        )

        consolidated_goals = ( 
            self.engine.consolidation_service 
            .consolidate( 
                goals
            )
        )

        return (
            consolidated_preferences
            + consolidated_goals
            + relevant_projects
        )
