import io
import json

import pytest
from PIL import Image

from processor import worker


def _png_bytes(size: tuple[int, int] = (800, 600)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color="red").save(buffer, format="PNG")
    return buffer.getvalue()


class _FakeBody:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data


class _FakeS3Client:
    def __init__(self, objects: dict[tuple[str, str], bytes]):
        self.objects = objects
        self.put_calls: list[dict] = []

    def get_object(self, Bucket, Key):  # noqa: N803
        return {"Body": _FakeBody(self.objects[(Bucket, Key)])}

    def put_object(self, Bucket, Key, Body, ContentType=None):  # noqa: N803
        self.put_calls.append(
            {"Bucket": Bucket, "Key": Key, "Body": Body, "ContentType": ContentType}
        )
        self.objects[(Bucket, Key)] = Body


class _FakeSQSClient:
    def __init__(self):
        self.deleted_receipt_handles: list[str] = []

    def delete_message(self, QueueUrl, ReceiptHandle):  # noqa: N803, ARG002
        self.deleted_receipt_handles.append(ReceiptHandle)


def _message(upload_id: str, bucket: str, key: str, receipt_handle: str = "receipt-1") -> dict:
    return {
        "Body": json.dumps({"upload_id": upload_id, "bucket": bucket, "key": key}),
        "ReceiptHandle": receipt_handle,
    }


@pytest.fixture(autouse=True)
def _stub_db(monkeypatch):
    calls = {"processing": [], "done": [], "failed": []}
    monkeypatch.setattr(
        worker, "mark_processing", lambda upload_id: calls["processing"].append(upload_id)
    )
    monkeypatch.setattr(
        worker,
        "mark_done",
        lambda upload_id, thumbnail_key: calls["done"].append((upload_id, thumbnail_key)),
    )
    monkeypatch.setattr(worker, "mark_failed", lambda upload_id: calls["failed"].append(upload_id))
    return calls


def test_make_thumbnail_shrinks_to_max_size():
    thumbnail_bytes, image_format = worker.make_thumbnail(_png_bytes((800, 600)))

    thumbnail = Image.open(io.BytesIO(thumbnail_bytes))
    assert image_format == "PNG"
    assert max(thumbnail.size) <= worker.THUMBNAIL_MAX_SIZE
    assert thumbnail.size[0] / thumbnail.size[1] == pytest.approx(800 / 600, rel=0.02)


def test_process_message_uploads_thumbnail_and_marks_done(_stub_db):
    s3 = _FakeS3Client({("uploads", "abc/cat.png"): _png_bytes()})

    worker.process_message(s3, {"upload_id": "abc", "bucket": "uploads", "key": "abc/cat.png"})

    assert _stub_db["processing"] == ["abc"]
    assert _stub_db["done"] == [("abc", "thumbnails/abc/cat.png")]
    assert s3.put_calls[0]["Key"] == "thumbnails/abc/cat.png"
    assert s3.put_calls[0]["ContentType"] == "image/png"


def test_handle_message_deletes_and_marks_done_on_success(_stub_db):
    s3 = _FakeS3Client({("uploads", "abc/cat.png"): _png_bytes()})
    sqs = _FakeSQSClient()

    worker.handle_message(sqs, s3, "http://fake/queue", _message("abc", "uploads", "abc/cat.png"))

    assert sqs.deleted_receipt_handles == ["receipt-1"]
    assert _stub_db["done"] == [("abc", "thumbnails/abc/cat.png")]
    assert _stub_db["failed"] == []


def test_handle_message_marks_failed_and_still_deletes_on_error(_stub_db):
    s3 = _FakeS3Client({})  # object missing -> get_object raises KeyError
    sqs = _FakeSQSClient()

    worker.handle_message(sqs, s3, "http://fake/queue", _message("missing", "uploads", "x.png"))

    assert _stub_db["failed"] == ["missing"]
    assert _stub_db["done"] == []
    assert sqs.deleted_receipt_handles == ["receipt-1"]
