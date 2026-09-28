from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class ForbiddenTerm(Base):
    """사내 보안 금지어 / 금지 문장.

    demo_dpi 기능에서 사용자가 입력한 질문에 포함될 경우, 로컬 LLM(Ollama)이
    문맥과 핵심 의미는 유지하되 아래 term 문자열이 그대로 노출되지 않도록
    유사 표현으로 재작성하는 데 사용된다.
    """

    __tablename__ = "forbidden_terms"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # WORD(단어) 또는 SENTENCE(문장)
    term_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="WORD"
    )

    # 실제 금지어/금지 문장
    term: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # 선택: 권장 대체 표현(있으면 재작성 힌트로 활용)
    replacement_hint: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    # 분류(사내보안, 프로젝트명, 인명 등)
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
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
