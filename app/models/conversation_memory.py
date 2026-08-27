from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversation.id"),
        unique=True,
        nullable=False
    )

    summary_md: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    current_goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    current_state: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    important_decisions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    next_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
