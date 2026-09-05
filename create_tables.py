from app.db.base import Base
from app.db.database import engine

import app.models.ai_prompt_run
import app.models.chat_history
import app.models.conversation
import app.models.conversation_memory
import app.models.memory_item
import app.models.response_format_template
import app.models.user

Base.metadata.create_all(bind=engine)

print("Tables Created")
