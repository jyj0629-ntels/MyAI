import os

from app.core.config import settings
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


def _normalize_database_url(database_url: str | None) -> str | None:
    if not database_url:
        return database_url

    return database_url.replace(
        "postgresql+psycopg2",
        "postgresql+psycopg",
    )


DATABASE_URL = _normalize_database_url(settings.DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
