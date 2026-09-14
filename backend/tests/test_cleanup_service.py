from datetime import UTC, datetime, timedelta

from backend.models.database import Upload, UploadStatus
from backend.services.cleanup_service import cleanup_stale_uploads


async def test_cleanup_marks_stale_pending_upload_expired_and_deletes_its_s3_object(
    db_session, _stub_aws_clients
):
    fake_s3, _ = _stub_aws_clients
    stale = Upload(
        filename="stale.png",
        status=UploadStatus.PENDING,
        created_at=datetime.now(UTC) - timedelta(minutes=60),
    )
    db_session.add(stale)
    await db_session.commit()
    await db_session.refresh(stale)
    fake_s3.objects[("test-bucket", f"{stale.id}/stale.png")] = (b"data", "image/png")

    expired_count = await cleanup_stale_uploads(db_session, older_than_minutes=30)

    assert expired_count == 1
    archived = await db_session.get(Upload, stale.id)
    assert archived is not None
    assert archived.status == UploadStatus.EXPIRED
    assert ("test-bucket", f"{stale.id}/stale.png") not in fake_s3.objects


async def test_cleanup_keeps_recent_pending_uploads_pending(db_session):
    recent = Upload(filename="recent.png", status=UploadStatus.PENDING)
    db_session.add(recent)
    await db_session.commit()
    await db_session.refresh(recent)

    expired_count = await cleanup_stale_uploads(db_session, older_than_minutes=30)

    assert expired_count == 0
    found = await db_session.get(Upload, recent.id)
    assert found.status == UploadStatus.PENDING


async def test_cleanup_ignores_non_pending_uploads(db_session):
    old_done = Upload(
        filename="done.png",
        status=UploadStatus.DONE,
        created_at=datetime.now(UTC) - timedelta(minutes=60),
    )
    db_session.add(old_done)
    await db_session.commit()
    await db_session.refresh(old_done)

    expired_count = await cleanup_stale_uploads(db_session, older_than_minutes=30)

    assert expired_count == 0
    found = await db_session.get(Upload, old_done.id)
    assert found.status == UploadStatus.DONE
