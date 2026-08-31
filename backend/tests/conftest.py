import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.main import app
from backend.models import Base
from backend.utils import aws_clients
from backend.utils.db_interface import engine, get_db


class _FakeS3Client:
    def __init__(self):
        self.objects: dict[tuple[str, str], tuple[bytes, str | None]] = {}

    def put_object(self, Bucket, Key, Body, ContentType=None):  # noqa: N803
        self.objects[(Bucket, Key)] = (Body, ContentType)
        return {}


class _FakeSQSClient:
    def __init__(self):
        self.sent_messages: list[tuple[str, str]] = []

    def send_message(self, QueueUrl, MessageBody):  # noqa: N803
        self.sent_messages.append((QueueUrl, MessageBody))
        return {"MessageId": "fake-message-id"}


@pytest.fixture(autouse=True)
def _stub_aws_clients(monkeypatch):
    """Uploads must not hit a real S3/SQS endpoint in tests — stand in for Floci."""
    fake_s3 = _FakeS3Client()
    fake_sqs = _FakeSQSClient()
    monkeypatch.setattr(aws_clients, "get_s3_client", lambda: fake_s3)
    monkeypatch.setattr(aws_clients, "get_sqs_client", lambda: fake_sqs)
    monkeypatch.setattr(
        aws_clients, "get_queue_url", lambda: "http://fake-floci:4566/000000000000/test-queue"
    )
    monkeypatch.setattr(aws_clients, "S3_BUCKET_NAME", "test-bucket")
    yield fake_s3, fake_sqs


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def db_session():
    """A session bound to a connection-level transaction that is rolled back
    after the test, so nothing written during a test is ever persisted.
    """
    async with engine.connect() as conn:
        await conn.begin()
        session_factory = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:
            yield session
        await conn.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
