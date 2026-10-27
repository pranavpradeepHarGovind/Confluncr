import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.config import get_settings
from app.main import app

settings = get_settings()
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", settings.DATABASE_URL)

test_engine = create_engine(
    TEST_DB_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure all tables exist before test session starts."""
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture(autouse=True)
def clean_database_tables():
    """Clean all tables before each test to guarantee test isolation."""
    with test_engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE transactions, accounts CASCADE;"))
        conn.commit()
    yield


@pytest.fixture
def db_session() -> Session:
    """Provides a dedicated database session for test queries."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Test client configured with clean DB dependency."""
    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
