import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME")


def get_s3_client():
    return boto3.client("s3", endpoint_url=AWS_ENDPOINT_URL, region_name=AWS_REGION)


def get_sqs_client():
    return boto3.client("sqs", endpoint_url=AWS_ENDPOINT_URL, region_name=AWS_REGION)


def get_queue_url(sqs_client) -> str:
    return sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)["QueueUrl"]
