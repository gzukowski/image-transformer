import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.upload_schema import GetAllUploadsResponse
from backend.utils.db_interface import get_db

api_router = APIRouter()
logger = logging.getLogger(__name__)


@api_router.get(
    "/uploads",
    response_model=GetAllUploadsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all uploaded files",
    tags=["uploads", "files"],
)
async def get_uploads(db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_uploads(db)
