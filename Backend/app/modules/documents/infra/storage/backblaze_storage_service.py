import asyncio
from typing import BinaryIO
import boto3
from botocore.config import Config
from app.core.config import settings
from app.modules.documents.domain.exception.exception import FileUploadError
from app.modules.documents.domain.repositories.storage_service import StorageService


class BackblazeB2StorageService(StorageService):
    def __init__(
        self,
        endpoint_url: str | None = None,
        key_id: str | None = None,
        application_key: str | None = None,
        bucket_name: str | None = None,
        region_name: str | None = None,
    ):
        self.endpoint_url = endpoint_url or settings.B2_ENDPOINT_URL
        self.key_id = key_id or settings.B2_APPLICATION_KEY_ID
        self.application_key = application_key or settings.B2_APPLICATION_KEY
        self.bucket_name = bucket_name or settings.B2_BUCKET_NAME
        self.region_name = region_name or settings.B2_REGION_NAME

    def _get_client(self):
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url or None,
            aws_access_key_id=self.key_id or None,
            aws_secret_access_key=self.application_key or None,
            region_name=self.region_name or None,
            config=Config(signature_version="s3v4"),
        )

    async def upload_file(self, file_obj: BinaryIO, file_key: str, content_type: str) -> None:
        def _upload():
            client = self._get_client()
            client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_key,
                ExtraArgs={"ContentType": content_type},
            )

        try:
            await asyncio.to_thread(_upload)
        except Exception as exc:
            raise FileUploadError(f"Failed to upload document to storage: {exc}") from exc

    def generate_presigned_view_url(self, file_key: str, expires_in: int = 3600) -> str:
        client = self._get_client()
        return client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": file_key,
                "ResponseContentType": "application/pdf",
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=expires_in,
        )

    def generate_presigned_download_url(self, file_key: str, file_name: str, expires_in: int = 3600) -> str:
        client = self._get_client()
        return client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": file_key,
                "ResponseContentDisposition": f'attachment; filename="{file_name}"',
            },
            ExpiresIn=expires_in,
        )
