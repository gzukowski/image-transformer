import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import Upload, UploadStatus
from backend.utils import aws_clients

logger = logging.getLogger(__name__)


async def cleanup_stale_uploads(db: AsyncSession, older_than_minutes: int) -> int:
    cutoff = datetime.now(UTC) - timedelta(minutes=older_than_minutes)
    result = await db.execute(
        select(Upload).where(Upload.status == UploadStatus.PENDING, Upload.created_at < cutoff)
    )
    stale_uploads = list(result.scalars().all())

    s3_client = aws_clients.get_s3_client()
    for upload in stale_uploads:
        key = f"{upload.id}/{upload.filename}"
        try:
            s3_client.delete_object(Bucket=aws_clients.S3_BUCKET_NAME, Key=key)
        except Exception:
            logger.exception("Failed to delete orphaned S3 object %s for upload %s", key, upload.id)
        # Marked expired rather than deleted, so stuck uploads stay visible for tracking.
        upload.status = UploadStatus.EXPIRED
        logger.info("Marked stale pending upload %s (%s) as expired", upload.id, upload.filename)

    await db.commit()
    return len(stale_uploads)
