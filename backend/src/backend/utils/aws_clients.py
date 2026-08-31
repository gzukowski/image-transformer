import os
from functools import lru_cache

import boto3

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME")


@lru_cache
def get_s3_client():
    return boto3.client("s3", endpoint_url=AWS_ENDPOINT_URL, region_name=AWS_REGION)


@lru_cache
def get_sqs_client():
    return boto3.client("sqs", endpoint_url=AWS_ENDPOINT_URL, region_name=AWS_REGION)


@lru_cache
def get_queue_url() -> str:
    return get_sqs_client().get_queue_url(QueueName=SQS_QUEUE_NAME)["QueueUrl"]
