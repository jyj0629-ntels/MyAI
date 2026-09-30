from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class TravelCompareHistory(Base):
    """A 2-round travel-comparison run.

    Round 1: personalized prompt -> each Public AI.
    Then Ollama synthesizes a Round 2 prompt from round-1 answers.
    Round 2: that prompt -> each Public AI, then Ollama produces the final guidance.
    """

    __tablename__ = "travel_compare_histories"

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

    round2_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    final_result: Mapped[str | None] = mapped_column(
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
