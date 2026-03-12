import asyncio
import logging
from datetime import datetime, timezone
from app.exceptions import DuplicateURLError
from app.repositories import metadata_repository as repo
from app.services.http_client import fetch_url
from app.schemas.metadata import MetadataResponse, MetadataAcceptedResponse

logger = logging.getLogger(__name__)

def build_response(doc):
    return MetadataResponse(
        id = str(doc["_id"]),
        url = doc["url"],
        headers = doc["headers"],
        cookies = doc["cookies"],
        page_source = doc["page_source"],
        status_code = doc["status_code"],
        status = doc["status"],
        created_at = doc["created_at"],
        updated_at = doc["updated_at"],
    )


async def create_metadata(url):
    existing = await repo.find_by_url(url)

    if existing is not None:
        raise DuplicateURLError(f"Metadata record already exists for URL: {url}")

    data = await fetch_url(url)

    document = {
        "url": url,
        "headers": data["headers"],
        "cookies": data["cookies"],
        "page_source": data["page_source"],
        "status_code": data["status_code"],
        "status": "collected",
        "error_message": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    inserted_id = await repo.insert(document)
    document["_id"] = inserted_id
    return build_response(document)


async def get_metadata(url):

    existing = await repo.find_by_url(url)

    if existing is not None and existing["status"] == "collected":
        return build_response(existing)
    
    if existing is not None and existing["status"] == "pending":
        return MetadataAcceptedResponse(url=url)
    
    was_inserted = await repo.insert_pending(url)
    if was_inserted:
        asyncio.create_task(collect_in_background(url))

    return MetadataAcceptedResponse(url=url)


async def collect_in_background(url):
    try:
        logger.info("Background collection started for: %s", url)
        data = await fetch_url(url)
        await repo.update_by_url(url, {
            "headers": data["headers"],
            "cookies": data["cookies"],
            "page_source": data["page_source"],
            "status_code": data["status_code"],
            "status": "collected",
            "error_message": None,
            "updated_at": datetime.now(timezone.utc),
        })
        logger.info("Background collection completed for: %s", url)
    
    except Exception as error:
        logger.error("Background collection failed for %s: %s", url, error)
        await repo.update_by_url(url, {
            "status": "failed",
            "error_message": str(error),
        })
    
