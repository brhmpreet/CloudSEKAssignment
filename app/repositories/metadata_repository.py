from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError, PyMongoError
from app.database.mongodb import get_database
import logging

logger = logging.getLogger(__name__)

async def find_by_url(url):
    db = get_database()
    document = await db.metadata.find_one({"url": url})
    return document


async def insert(document):
    db = get_database()
    result = await db.metadata.insert_one(document)
    return str(result.inserted_id)


async def update_by_url(url, new_values):
    db = get_database()
    result = await db.metadata.update_one({"url": url}, {"$set": new_values})
    return result.modified_count > 0


async def insert_pending(url):
    try:
        db = get_database()
        now = datetime.now(timezone.utc)
        await db.metadata.insert_one({
            "url": url,
            "headers": {},
            "cookies": {},
            "page_source": "",
            "status_code": 0,
            "status": "pending",
            "error_message": None,
            "created_at": now,
            "updated_at": now,
        })
        return True
    except DuplicateKeyError:
        return False

async def update_status_by_url(url, status):
    try:
        db = get_database()
        now = datetime.now(timezone.utc)
        await db.metadata.update_one({"url": url}, {"$set": {"status": status, "updated_at": now}})
        return True
    except PyMongoError as error:
        logger.error("Failed to update status for URL: %s: %s", url, error)
        return False
        