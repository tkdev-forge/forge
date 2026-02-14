import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
for path in (str(BACKEND_ROOT), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

TEST_DB = Path("/tmp/forge_test.db")
os.environ.setdefault("DATABASE_URL", f"sqlite+pysqlite:///{TEST_DB}")
os.environ.setdefault("JWT_REQUIRED", "false")
os.environ.setdefault("ENVIRONMENT", "development")

from database import Base, SessionLocal, engine, get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def _override_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}
