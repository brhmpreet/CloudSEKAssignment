from datetime import datetime
from pydantic import BaseModel, HttpUrl

class MetadataCreateRequest(BaseModel):
    url: HttpUrl


class MetadataResponse(BaseModel):
    id: str
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    status_code: int
    status: str
    created_at: datetime
    updated_at: datetime

class MetadataAcceptedResponse(BaseModel):
    url: str
    status: str = "pending"
    message: str = "Metadata collection has been initiated. Please retry shortly."