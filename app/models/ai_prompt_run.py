from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class AIPromptRun(Base):
    __tablename__ = "ai_prompt_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    conversation_id: Mapped[int | None] = mapped_column(
        ForeignKey("conversation.id"),
        nullable=True
    )

    selected_provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    selected_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    strategy_md: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    final_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
