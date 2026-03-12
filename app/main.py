from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from contextlib import asynccontextmanager
from app.config import settings
from app.database.mongodb import connect_to_mongodb, disconnect_from_mongodb
from app.exceptions import DuplicateURLError, URLFetchError, URLTimeoutError
from app.api.routes.metadata import router as metadata_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb(settings.mongo_uri, settings.mongo_db_name)
    print("Connected to MongoDB")

    yield

    await disconnect_from_mongodb()
    print("Disconnected from MongoDB")


app = FastAPI(title="HTTP Metadata Inventory Service", version="1.0.0", lifespan=lifespan)

app.include_router(metadata_router, prefix="/api/v1/metadata", tags=["metadata"])


@app.exception_handler(DuplicateURLError)
async def handle_duplicate(request: Request, error: DuplicateURLError):
    return JSONResponse(status_code=409, content={"detail": str(error)})

@app.exception_handler(URLFetchError)
async def handle_fetch_error(request: Request, error: URLFetchError):
    return JSONResponse(status_code=502, content={"detail": str(error)})

@app.exception_handler(URLTimeoutError)
async def handle_timeout(request: Request, error: URLTimeoutError):
    return JSONResponse(status_code=504, content={"detail": str(error)})


@app.get("/health")
async def health_check():
    return {"status": "ok"}