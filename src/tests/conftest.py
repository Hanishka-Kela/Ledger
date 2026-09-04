import pytest

from fastapi.testclient import TestClient

from src.infrastructure.database.base import Base
from src.tests.test_database import test_engine, TestSessionLocal

from src.main import app
from src.api.dependencies import get_db


@pytest.fixture
def db_session():
    Base.metadata.create_all(test_engine)

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)


@pytest.fixture
def client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()