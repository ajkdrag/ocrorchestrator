import json
import shutil
from pathlib import Path
from typing import Any, Dict

import yaml

from .base import BaseRepo


class LocalRepo(BaseRepo):
    def _get_yaml(self, path: str) -> Dict[str, Any]:
        full_path = Path(self.remote_path) / path
        with open(full_path, "r") as file:
            return yaml.safe_load(file)

    def _get_json(self, path: str) -> Dict[str, Any]:
        full_path = Path(self.remote_path) / path
        with open(full_path, "r") as file:
            return json.load(file)

    def _get_text(self, path: str) -> str:
        full_path = Path(self.remote_path) / path
        with open(full_path, "r") as file:
            return file.read()

    def _download_obj(self, path: str) -> None:
        src_path = Path(self.remote_path) / path
        local_file_path = self.local_dir / path
        local_file_path.parent.mkdir(parents=True, exist_ok=True)

        if not local_file_path.exists():
            shutil.copy2(src_path, local_file_path)

        return str(local_file_path)
