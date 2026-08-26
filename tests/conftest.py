import pytest
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app


@pytest.fixture
def client() -> Generator:
    with TestClient(app) as test_client:
        yield test_client