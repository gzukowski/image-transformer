from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.models.database import UploadStatus


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: UploadStatus
    thumbnail_url: str | None
    created_at: datetime


class GetAllUploadsResponse(BaseModel):
    uploads: list[UploadResponse]
