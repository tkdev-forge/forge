from collections.abc import Mapping, Sequence

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_safe_query(
    db: Session, query: str, params: Mapping[str, object] | None = None
) -> Sequence[object]:
    """Executes parameterized SQL only to prevent SQL injection from interpolated strings."""
    statement = text(query)
    result = db.execute(statement, params or {})
    return result.fetchall()
