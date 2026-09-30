from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class TravelRoundResponse(Base):
    """One Public AI's response for a given round (1 or 2) of a TravelCompareHistory."""

    __tablename__ = "travel_round_responses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    history_id: Mapped[int] = mapped_column(
        ForeignKey("travel_compare_histories.id"),
        nullable=False
    )

    round_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    ai_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    raw_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SUCCESS"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
