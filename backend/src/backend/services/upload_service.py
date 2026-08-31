import json
import logging
import uuid
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import Upload
from backend.utils import aws_clients
from backend.utils.constants import ALLOWED_UPLOAD_CONTENT_TYPES, MAX_UPLOAD_SIZE_BYTES
from backend.utils.exceptions import _raise_http

logger = logging.getLogger(__name__)


async def create_upload(db: AsyncSession, file: UploadFile) -> Upload:
    if not file.filename:
        _raise_http(status.HTTP_400_BAD_REQUEST, "Missing filename")
    if file.content_type not in ALLOWED_UPLOAD_CONTENT_TYPES:
        _raise_http(status.HTTP_400_BAD_REQUEST, f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        _raise_http(status.HTTP_400_BAD_REQUEST, "File too large")

    upload_id = uuid.uuid4()
    key = f"{upload_id}/{file.filename}"

    aws_clients.get_s3_client().put_object(
        Bucket=aws_clients.S3_BUCKET_NAME,
        Key=key,
        Body=contents,
        ContentType=file.content_type,
    )

    upload = Upload(id=upload_id, filename=file.filename)
    db.add(upload)
    await db.commit()
    await db.refresh(upload)

    aws_clients.get_sqs_client().send_message(
        QueueUrl=aws_clients.get_queue_url(),
        MessageBody=json.dumps(
            {"upload_id": str(upload.id), "bucket": aws_clients.S3_BUCKET_NAME, "key": key}
        ),
    )

    logger.info("Created upload %s (%s), s3 key=%s", upload.id, upload.filename, key)
    return upload


async def get_uploads(db: AsyncSession) -> list[Upload]:
    result = await db.execute(select(Upload).order_by(Upload.created_at.desc()))
    return list(result.scalars().all())


async def get_upload(db: AsyncSession, upload_id: UUID) -> Upload:
    upload = await db.get(Upload, upload_id)
    if upload is None:
        _raise_http(status.HTTP_404_NOT_FOUND, f"Upload {upload_id} not found")
    return upload
