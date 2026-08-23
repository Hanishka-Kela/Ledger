import pytest

from src.infrastructure.database.base import Base
from src.tests.test_database import test_engine, TestSessionLocal


@pytest.fixture
def db_session():
    Base.metadata.create_all(test_engine)

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)