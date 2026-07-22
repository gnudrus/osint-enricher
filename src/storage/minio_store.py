"""MinIO (S3-compatible) storage backend."""
import os
import boto3
from botocore.client import Config
from .base import BaseStorage

class MinIOStore(BaseStorage):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
    ):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            verify=secure,
        )

    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        self.s3.put_object(Bucket=bucket, Key=key, Body=data)

    def get_object(self, bucket: str, key: str) -> bytes:
        resp = self.s3.get_object(Bucket=bucket, Key=key)
        return resp["Body"].read()

    def list_objects(self, bucket: str, prefix: str = ""):
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                yield obj["Key"]

    def delete_object(self, bucket: str, key: str) -> None:
        self.s3.delete_object(Bucket=bucket, Key=key)
