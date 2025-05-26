import pytest
from starlette.testclient import TestClient

from app.main import create_api


@pytest.fixture(scope="session")
def client():
    app = create_api().app
    with TestClient(app) as client:
        yield client
