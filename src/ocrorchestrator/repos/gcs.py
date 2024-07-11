import json
from typing import Any, Dict, List

import yaml

from .base import BaseRepo


class GCSRepo(BaseRepo):
    def __init__(self, remote_path: str, local_dir: str):
        from google.cloud import storage

        super().__init__(remote_path, local_dir)
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.remote_path)

    def _get_yaml(self, path: str) -> Dict[str, Any]:
        blob = self.bucket.blob(path)
        content = blob.download_as_text()
        return yaml.safe_load(content)

    def _get_json(self, path: str) -> Dict[str, Any]:
        blob = self.bucket.blob(path)
        content = blob.download_as_text()
        return json.loads(content)

    def _get_text(self, path: str) -> str:
        blob = self.bucket.blob(path)
        return blob.download_as_text()

    def _get_binary(self, path: str) -> bytes:
        blob = self.bucket.blob(path)
        return blob.download_as_bytes()

    def _list_directory(self, path: str) -> List[str]:
        prefix = path.rstrip("/") + "/"
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter="/")
        files = []
        for blob in blobs:
            if blob.name != prefix:  # Exclude the directory itself
                file_path = blob.name[len(prefix) :]
                if (
                    "/" not in file_path
                ):  # Only include files in the immediate directory
                    files.append(blob.name)
        return files

    def _download_obj(self, path: str) -> str:
        blob = self.bucket.blob(path)
        local_file_path = self.local_dir / path
        local_file_path.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(str(local_file_path))
        return str(local_file_path)
