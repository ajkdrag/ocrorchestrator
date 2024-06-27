from typing import Any, Dict

import yaml
from google.cloud import storage


class GCSUtils:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def get_yaml(self, blob_name: str) -> Dict[str, Any]:
        blob = self.bucket.blob(blob_name)
        content = blob.download_as_text()
        return yaml.safe_load(content)

    def get_text(self, blob_name: str) -> str:
        blob = self.bucket.blob(blob_name)
        return blob.download_as_text()

    def download_model(self, blob_name: str, destination_file_name: str):
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(destination_file_name)
