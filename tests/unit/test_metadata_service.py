import pytest 
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from app.schemas.metadata import MetadataResponse, MetadataAcceptedResponse

FAKE_URL = "https://example.com/"

def make_fake_document(url=FAKE_URL, status="collected"):
    now = datetime.now(timezone.utc)
    return {
        "_id": "abc123",
        "url": url,
        "headers": {"content-type": "text/html"},
        "cookies": {},
        "page_source": "<html></html>",
        "status_code": 200,
        "status": status,
        "error_message": None,
        "created_at": now,
        "updated_at": now,
    }


def make_fake_fetch_result():
    return {
        "headers": {"content-type": "text/html"},
        "cookies": {},
        "page_source": "<html></html>",
        "status_code": 200,
    }


@patch("app.services.metadata_service.fetch_url")
@patch("app.services.metadata_service.repo")
async def test_create_metadata_success(fake_repo, fake_fetch):
    fake_repo.find_by_url = AsyncMock(return_value=None)
    fake_repo.insert = AsyncMock(return_value="new_id_123")
    fake_fetch.return_value = make_fake_fetch_result()

    from app.services.metadata_service import create_metadata
    result = await create_metadata(FAKE_URL)

    assert isinstance(result, MetadataResponse)
    assert result.url == FAKE_URL
    assert result.status == "collected"


@patch("app.services.metadata_service.asyncio")
@patch("app.services.metadata_service.repo")
async def test_get_metadata_missing_triggers_background(fake_repo, fake_asyncio):
    fake_repo.find_by_url = AsyncMock(return_value=None)
    fake_repo.insert_pending = AsyncMock(return_value=True)

    from app.services.metadata_service import get_metadata
    result = await get_metadata(FAKE_URL)

    assert isinstance(result, MetadataAcceptedResponse)

    fake_asyncio.create_task.assert_called_once()