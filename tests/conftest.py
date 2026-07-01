import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.ingestion import get_db as get_db_ingestion
from app.api.v1.workflow import get_db as get_db_workflow
from app.db.database import Base
from app.main import app

# We need to override the get_db dependency for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_ingestion] = override_get_db
app.dependency_overrides[get_db_workflow] = override_get_db


@pytest.fixture(scope="module")
def client():
    # Setup test database tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Teardown
    Base.metadata.drop_all(bind=engine)
