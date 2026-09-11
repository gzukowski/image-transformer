import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.upload_schema import GetAllUploadsResponse, UploadResponse
from backend.services import upload_service
from backend.utils.db_interface import get_db

api_router = APIRouter(prefix="/uploads", tags=["uploads"])
logger = logging.getLogger(__name__)


@api_router.get(
    "",
    response_model=GetAllUploadsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all uploaded files",
)
async def list_uploads(db: Annotated[AsyncSession, Depends(get_db)]):
    uploads = await upload_service.get_uploads(db)
    return GetAllUploadsResponse(uploads=uploads)


@api_router.get(
    "/{upload_id}",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single upload by id",
)
async def get_upload(upload_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    return await upload_service.get_upload(db, upload_id)


@api_router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new upload",
)
async def create_upload(file: UploadFile, db: Annotated[AsyncSession, Depends(get_db)]):
    return await upload_service.create_upload(db, file)


@api_router.get(
    "/{upload_id}/thumbnail",
    status_code=status.HTTP_200_OK,
    summary="Stream the generated thumbnail for a completed upload",
)
async def get_upload_thumbnail(upload_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    body, content_type = await upload_service.get_upload_thumbnail(db, upload_id)
    return StreamingResponse(body.iter_chunks(), media_type=content_type)
