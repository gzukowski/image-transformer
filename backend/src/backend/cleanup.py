import asyncio
import logging

from backend.services.cleanup_service import cleanup_stale_uploads
from backend.utils.constants import STALE_UPLOAD_MINUTES
from backend.utils.db_interface import SessionLocal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(module)s - %(message)s",
)
logging.getLogger("botocore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def _run() -> None:
    async with SessionLocal() as db:
        expired_count = await cleanup_stale_uploads(db, STALE_UPLOAD_MINUTES)
    logger.info("Cleanup complete: marked %d stale pending upload(s) as expired", expired_count)


def main() -> None:
    asyncio.run(_run())
