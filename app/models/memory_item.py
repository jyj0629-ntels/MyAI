from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    key: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    importance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5
    )

    freshness: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    source_conversation_id: Mapped[int | None] = mapped_column(
        ForeignKey("conversation.id"),
        nullable=True
    )

    source_chat_history_id: Mapped[int | None] = mapped_column(
        ForeignKey("chat_history.id"),
        nullable=True
    )

    scope: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="CANDIDATE"
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    last_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
