from typing import Any, Dict

import yaml

from .base import BaseRepo


class GCSRepo(BaseRepo):
    def __init__(self, bucket_name: str):
        from google.cloud import storage

        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def get_yaml(self, path: str) -> Dict[str, Any]:
        blob = self.bucket.blob(path)
        content = blob.download_as_text()
        return yaml.safe_load(content)

    def get_text(self, path: str) -> str:
        blob = self.bucket.blob(path)
        return blob.download_as_text()

    def download_obj(self, path: str, local_path: str) -> None:
        blob = self.bucket.blob(path)
        blob.download_to_filename(local_path)
