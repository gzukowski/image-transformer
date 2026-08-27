import logging
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import Upload
from backend.utils.constants import ALLOWED_UPLOAD_CONTENT_TYPES
from backend.utils.exceptions import _raise_http

logger = logging.getLogger(__name__)


async def create_upload(db: AsyncSession, file: UploadFile) -> Upload:
    if not file.filename:
        _raise_http(status.HTTP_400_BAD_REQUEST, "Missing filename")
    if file.content_type not in ALLOWED_UPLOAD_CONTENT_TYPES:
        _raise_http(status.HTTP_400_BAD_REQUEST, f"Unsupported file type: {file.content_type}")

    upload = Upload(filename=file.filename)
    db.add(upload)
    await db.commit()
    await db.refresh(upload)
    logger.info("Created upload %s (%s)", upload.id, upload.filename)
    return upload


async def get_uploads(db: AsyncSession) -> list[Upload]:
    result = await db.execute(select(Upload).order_by(Upload.created_at.desc()))
    return list(result.scalars().all())


async def get_upload(db: AsyncSession, upload_id: UUID) -> Upload:
    upload = await db.get(Upload, upload_id)
    if upload is None:
        _raise_http(status.HTTP_404_NOT_FOUND, f"Upload {upload_id} not found")
    return upload
