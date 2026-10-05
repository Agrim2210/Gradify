from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, file_obj: BinaryIO, file_key: str, content_type: str) -> None:
        pass

    @abstractmethod
    def generate_presigned_view_url(self, file_key: str, expires_in: int = 3600) -> str:
        pass

    @abstractmethod
    def generate_presigned_download_url(self, file_key: str, file_name: str, expires_in: int = 3600) -> str:
        pass
