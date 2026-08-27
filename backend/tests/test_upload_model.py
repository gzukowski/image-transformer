from backend.models.database import Upload, UploadStatus


async def test_upload_defaults_to_pending_status_and_utc_created_at(db_session):
    upload = Upload(filename="x.png")
    db_session.add(upload)
    await db_session.commit()
    await db_session.refresh(upload)

    assert upload.status == UploadStatus.PENDING
    assert upload.thumbnail_url is None
    assert upload.created_at.tzinfo is not None
    assert upload.created_at.utcoffset().total_seconds() == 0
