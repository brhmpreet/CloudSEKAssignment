import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.database import mongodb as mongodb_module
from app.main import app

@pytest.fixture()
async def async_client():

    fake_client = AsyncMongoMockClient()
    fake_db = fake_client["test_db"]
    await fake_db.metadata.create_index("url", unique=True)

    with patch.object(mongodb_module, "db", fake_db):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
