from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class CompareHistory(Base):
    """A single /demo_compare run: the user question and the final cross-checked summary."""

    __tablename__ = "compare_histories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    user_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    summary_result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    llm_model_used: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PROCESSING"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
