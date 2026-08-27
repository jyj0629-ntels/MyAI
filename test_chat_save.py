from app.db.database import SessionLocal
from app.repositories.chat_repository import ChatRepository

db = SessionLocal()

repo = ChatRepository(db)

repo.save(
    provider="test",
    model="test-model",
    question="save test",
    answer="saved"
)

print("saved")
