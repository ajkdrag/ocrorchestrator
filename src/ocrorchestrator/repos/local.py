import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

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

    def _get_binary(self, path: str) -> bytes:
        full_path = Path(self.remote_path) / path
        with open(full_path, "rb") as file:
            return file.read()

    def _list_directory(self, path: str) -> List[str]:
        full_path = Path(self.remote_path) / path
        return [str(Path(path) / f.name) for f in full_path.iterdir() if f.is_file()]

    def _download_obj(self, path: str, overwrite=False) -> str:
        src_path = Path(self.remote_path) / path
        local_file_path = self.local_dir / path
        local_file_path.parent.mkdir(parents=True, exist_ok=True)
        if local_file_path.exists() and not overwrite:
            return str(local_file_path)
        shutil.copy2(src_path, local_file_path)
        return str(local_file_path)

    def _save_file(self, path: str, content: str) -> str:
        full_path = Path(self.remote_path) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as file:
            file.write(content)
        return str(full_path)