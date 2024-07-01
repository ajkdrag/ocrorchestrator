from typing import Any, Dict, Optional

import yaml

from .base import BaseRepo


class LocalRepo(BaseRepo):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def get_yaml(self, path: str) -> Dict[str, Any]:
        full_path = f"{self.base_path}/{path}"
        with open(full_path, "r") as file:
            return yaml.safe_load(file)

    def get_text(self, path: str) -> str:
        full_path = f"{self.base_path}/{path}"
        with open(full_path, "r") as file:
            return file.read()

    def download_obj(self, path: str, local_path: Optional[str] = None) -> None:
        full_path = f"{self.base_path}/{path}"
        return full_path
