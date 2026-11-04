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

    feature: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="myai",
        default="myai"
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

    provider_response_path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None
    )

    # Local LLM이 선호도를 반영해 만든 프롬프트(이력 클릭 시 UI에 복원).
    generated_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    # Public AI별 응답(JSON). 컨테이너 재생성으로 md 파일이 사라져도 팝업이 복원되도록 DB에 보관.
    provider_responses_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
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
