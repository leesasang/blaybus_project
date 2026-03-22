from __future__ import annotations

import mimetypes

import boto3
from botocore.client import Config

from app.core.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET_NAME,
    R2_ENDPOINT,
    R2_PUBLIC_BASE_URL,
    R2_SECRET_ACCESS_KEY,
)
from app.services.storage.base import StorageService


class R2StorageService(StorageService):
    def __init__(self) -> None:
        self.bucket_name = R2_BUCKET_NAME
        self.endpoint = R2_ENDPOINT
        self.public_base_url = R2_PUBLIC_BASE_URL

        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

    def save_file(self, *, data: bytes, relative_path: str) -> dict:
        content_type, _ = mimetypes.guess_type(relative_path)
        if not content_type:
            content_type = "application/octet-stream"

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=relative_path,
            Body=data,
            ContentType=content_type,
        )

        public_url = None
        if self.public_base_url:
            public_url = f"{self.public_base_url.rstrip('/')}/{relative_path}"

        return {
            "storage_provider": "r2",
            "storage_path": relative_path,
            "public_url": public_url,
            "content_type": content_type,
            "size_bytes": len(data),
        }

    def delete_file(self, *, relative_path: str) -> None:
        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=relative_path,
        )
