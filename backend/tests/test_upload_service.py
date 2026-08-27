import asyncio
import io
import uuid

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from backend.models.database import UploadStatus
from backend.services import upload_service


def _make_upload_file(filename: str | None, content_type: str) -> UploadFile:
    return UploadFile(
        file=io.BytesIO(b"fake-bytes"),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


async def test_create_upload_persists_pending_record(db_session):
    upload = await upload_service.create_upload(
        db_session, _make_upload_file("cat.png", "image/png")
    )

    assert upload.filename == "cat.png"
    assert upload.status == UploadStatus.PENDING
    assert upload.thumbnail_url is None


async def test_create_upload_rejects_unsupported_content_type(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await upload_service.create_upload(db_session, _make_upload_file("doc.txt", "text/plain"))

    assert exc_info.value.status_code == 400


async def test_create_upload_rejects_missing_filename(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await upload_service.create_upload(db_session, _make_upload_file(None, "image/png"))

    assert exc_info.value.status_code == 400


async def test_get_uploads_returns_newest_first(db_session):
    first = await upload_service.create_upload(db_session, _make_upload_file("a.png", "image/png"))
    await asyncio.sleep(0.01)  # ensure a distinct created_at from clock-resolution ties
    second = await upload_service.create_upload(db_session, _make_upload_file("b.png", "image/png"))

    uploads = await upload_service.get_uploads(db_session)

    assert [u.id for u in uploads] == [second.id, first.id]


async def test_get_upload_returns_matching_record(db_session):
    created = await upload_service.create_upload(
        db_session, _make_upload_file("c.png", "image/png")
    )

    found = await upload_service.get_upload(db_session, created.id)

    assert found.id == created.id


async def test_get_upload_raises_404_when_missing(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await upload_service.get_upload(db_session, uuid.uuid4())

    assert exc_info.value.status_code == 404
