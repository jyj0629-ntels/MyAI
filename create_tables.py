from app.db.base import Base
from app.db.database import engine

import app.models.user
import app.models.chat_history


Base.metadata.create_all(bind=engine)

print("Tables Created")
