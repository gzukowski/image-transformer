import logging

from processor.aws_clients import get_queue_url, get_s3_client, get_sqs_client
from processor.worker import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(module)s - %(message)s",
)
logging.getLogger("botocore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Processor starting up")

    sqs_client = get_sqs_client()
    s3_client = get_s3_client()
    queue_url = get_queue_url(sqs_client)

    run(sqs_client, s3_client, queue_url)
