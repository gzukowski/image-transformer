import uuid

from backend.services import upload_service

PNG_BYTES = b"\x89PNG\r\n\x1a\n"


async def test_create_upload_returns_201(client):
    files = {"file": ("cat.png", PNG_BYTES, "image/png")}

    response = await client.post("/uploads", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "cat.png"
    assert body["status"] == "pending"
    assert body["thumbnail_url"] is None


async def test_create_upload_rejects_unsupported_type(client):
    files = {"file": ("doc.txt", b"hello", "text/plain")}

    response = await client.post("/uploads", files=files)

    assert response.status_code == 400


async def test_list_uploads_includes_created_upload(client):
    files = {"file": ("dog.png", PNG_BYTES, "image/png")}
    created = (await client.post("/uploads", files=files)).json()

    response = await client.get("/uploads")

    assert response.status_code == 200
    ids = [u["id"] for u in response.json()["uploads"]]
    assert created["id"] in ids


async def test_get_upload_by_id_returns_record(client):
    files = {"file": ("bird.png", PNG_BYTES, "image/png")}
    created = (await client.post("/uploads", files=files)).json()

    response = await client.get(f"/uploads/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_upload_by_id_returns_404_when_missing(client):
    response = await client.get(f"/uploads/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_get_upload_thumbnail_streams_bytes(client, db_session, _stub_aws_clients):
    fake_s3, _ = _stub_aws_clients
    files = {"file": ("owl.png", PNG_BYTES, "image/png")}
    created = (await client.post("/uploads", files=files)).json()

    thumbnail_key = f"thumbnails/{created['id']}/owl.png"
    fake_s3.put_object(
        Bucket="test-bucket", Key=thumbnail_key, Body=b"thumb-bytes", ContentType="image/png"
    )
    upload = await upload_service.get_upload(db_session, uuid.UUID(created["id"]))
    upload.thumbnail_url = thumbnail_key
    await db_session.commit()

    response = await client.get(f"/uploads/{created['id']}/thumbnail")

    assert response.status_code == 200
    assert response.content == b"thumb-bytes"
    assert response.headers["content-type"] == "image/png"


async def test_get_upload_thumbnail_returns_404_before_processing(client):
    files = {"file": ("owl.png", PNG_BYTES, "image/png")}
    created = (await client.post("/uploads", files=files)).json()

    response = await client.get(f"/uploads/{created['id']}/thumbnail")

    assert response.status_code == 404
