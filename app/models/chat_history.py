from datetime import datetime

from sqlalchemy import func
from sqlalchemy import DateTime
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base

from sqlalchemy import ForeignKey


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    conversation_id: Mapped[int | None] = mapped_column(
        ForeignKey("conversation.id"),
        nullable=True
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    input_tokens: Mapped[int | None] = mapped_column(
        nullable=True
    )

    output_tokens: Mapped[int | None] = mapped_column(
        nullable=True
    )

    success: Mapped[bool] = mapped_column( 
        nullable=False, 
        default=True
    ) 
