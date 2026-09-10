import io
import json
import logging
import os

from PIL import Image

from processor.db import mark_done, mark_failed, mark_processing

logger = logging.getLogger(__name__)

THUMBNAIL_MAX_SIZE = int(os.getenv("THUMBNAIL_MAX_SIZE", "256"))
POLL_WAIT_SECONDS = 20


def make_thumbnail(image_bytes: bytes) -> tuple[bytes, str]:
    image = Image.open(io.BytesIO(image_bytes))
    image_format = image.format or "PNG"
    image.thumbnail((THUMBNAIL_MAX_SIZE, THUMBNAIL_MAX_SIZE))

    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue(), image_format


def process_message(s3_client, body: dict) -> None:
    upload_id = body["upload_id"]
    bucket = body["bucket"]
    key = body["key"]

    mark_processing(upload_id)

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    thumbnail_bytes, image_format = make_thumbnail(obj["Body"].read())

    thumbnail_key = f"thumbnails/{key}"
    s3_client.put_object(
        Bucket=bucket,
        Key=thumbnail_key,
        Body=thumbnail_bytes,
        ContentType=f"image/{image_format.lower()}",
    )

    mark_done(upload_id, thumbnail_key)
    logger.info("Processed upload %s -> %s", upload_id, thumbnail_key)


def handle_message(sqs_client, s3_client, queue_url: str, message: dict) -> None:
    body = json.loads(message["Body"])
    try:
        process_message(s3_client, body)
    except Exception:
        logger.exception("Failed to process upload %s", body.get("upload_id"))
        mark_failed(body.get("upload_id"))
    sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])


def run(sqs_client, s3_client, queue_url: str) -> None:
    logger.info("Polling queue %s", queue_url)

    while True:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=POLL_WAIT_SECONDS,
        )

        for message in response.get("Messages", []):
            handle_message(sqs_client, s3_client, queue_url, message)
