from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRepo(ABC):
    @abstractmethod
    def get_yaml(self, path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_text(self, path: str) -> str:
        pass

    @abstractmethod
    def download_obj(self, path: str, local_path: str) -> None:
        pass
