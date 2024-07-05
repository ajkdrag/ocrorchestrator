import functools
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict

import structlog

from ..datamodels.api_io import AppException
from ..utils.constants import ErrorCode

log = structlog.get_logger()


def repo_error_handler(func: Callable):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            error_code = (
                ErrorCode.REPO_GET_ERROR
                if func.__name__.startswith("get_")
                else ErrorCode.REPO_OBJECT_DOWNLOAD_ERROR
            )
            log.error(
                f"Repo operation error in {func.__name__}",
                status_code=error_code.status_code,
                status=error_code.name,
                exc_info=True,
            )
            raise RepoException(error_code, traceback.format_exc()) from e

    return wrapper


class BaseRepo(ABC):
    def __init__(self, remote_path: str, local_dir: str):
        self.remote_path = remote_path
        self.local_dir = Path(local_dir).resolve()
        self.local_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _get_yaml(self, path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_json(self, path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_text(self, path: str) -> str:
        pass

    @abstractmethod
    def _download_obj(self, path: str) -> None:
        pass

    @repo_error_handler
    def get_obj(self, path: str) -> str:
        if path.endswith(".yaml"):
            return self._get_yaml(path)
        elif path.endswith(".json"):
            return self._get_json(path)
        return self._get_text(path)

    @repo_error_handler
    def download_obj(self, path: str) -> None:
        return self._download_obj(path)


class RepoException(AppException):
    pass
