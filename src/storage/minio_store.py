"""MinIO/S3-compatible storage backend."""

from __future__ import annotations

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .base import BaseStorage


class MinIOStore(BaseStorage):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            verify=secure,
        )

    def _ensure_bucket(self, bucket: str) -> None:
        try:
            self.s3.head_bucket(Bucket=bucket)
        except ClientError as exc:
            status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if status not in {403, 404}:
                raise
            if status == 403:
                raise
            self.s3.create_bucket(Bucket=bucket)

    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        self._ensure_bucket(bucket)
        self.s3.put_object(Bucket=bucket, Key=key, Body=data)

    def get_object(self, bucket: str, key: str) -> bytes:
        return self.s3.get_object(Bucket=bucket, Key=key)["Body"].read()

    def list_objects(self, bucket: str, prefix: str = ""):
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                yield item["Key"]

    def delete_object(self, bucket: str, key: str) -> None:
        self.s3.delete_object(Bucket=bucket, Key=key)
