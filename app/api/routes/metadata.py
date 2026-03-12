from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl

from app.schemas.metadata import MetadataCreateRequest, MetadataResponse, MetadataAcceptedResponse
from app.services import metadata_service

router = APIRouter()

@router.post("/", status_code=201, response_model=MetadataResponse)
async def create_metadata(request: MetadataCreateRequest):
    """Create a metadata record for a URL."""
    result  = await metadata_service.create_metadata(str(request.url))
    return result

@router.get("/")
async def get_metadata(url: HttpUrl = Query(...)):

    result = await metadata_service.get_metadata(str(url))

    if isinstance(result, MetadataAcceptedResponse):
        return JSONResponse(status_code=202, content=result.model_dump())

    return result