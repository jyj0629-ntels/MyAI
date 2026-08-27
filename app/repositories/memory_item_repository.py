from app.models.memory_item import MemoryItem


class MemoryItemRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        memory_item: MemoryItem
    ):

        self.db.add(memory_item)
        self.db.commit()
        self.db.refresh(memory_item)

        return memory_item

    def get_by_user(
        self,
        user_id: int
    ):

        return (
            self.db.query(MemoryItem)
            .filter(
                MemoryItem.user_id == user_id
            )
            .all()
        )

    def get_by_type(
        self,
        user_id: int,
        memory_type: str
    ):

        return (
            self.db.query(MemoryItem)
            .filter(
                MemoryItem.user_id == user_id,
                MemoryItem.type == memory_type
            )
            .all()
        )

    def get_active_memories(
        self,
        user_id: int
    ):

        return (
            self.db.query(MemoryItem)
            .filter(
                MemoryItem.user_id == user_id,
                MemoryItem.status == "ACTIVE"
            )
            .all()
        )
    def get_by_key(
        self,
        user_id: int,
        memory_key: str
    ):

        return (
            self.db.query(MemoryItem)
            .filter(
                MemoryItem.user_id == user_id,
                MemoryItem.key == memory_key
            )
            .first()
        )
    def exists_by_key(
        self,
        user_id: int,
        memory_key: str
    ):

        return (
            self.db.query(MemoryItem)
            .filter(
                MemoryItem.user_id == user_id,
                MemoryItem.key == memory_key
            )
            .first()
        )

    def update(
        self,
        memory
    ):

        self.db.commit()

        self.db.refresh(
            memory
        )

        return memory
