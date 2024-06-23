import pytest
from fastapi.testclient import TestClient

from fastzero.app import app


@pytest.fixture()
def client():
    return TestClient(app)
