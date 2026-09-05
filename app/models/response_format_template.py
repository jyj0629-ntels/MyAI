from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResponseFormatTemplate(Base):
    __tablename__ = "response_format_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    template_text: Mapped[str] = mapped_column(Text, nullable=False)

    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
