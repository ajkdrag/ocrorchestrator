import base64
import functools
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List

import fitz
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
    def _get_binary(self, path: str) -> bytes:
        pass

    def _get_image(self, path: str) -> str:
        image_data = self._get_binary(path)
        return base64.b64encode(image_data).decode("utf-8")

    def _get_pdf(self, path: str) -> str:
        pdf_data = self._get_binary(path)
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        if len(pdf_document) > 0:
            first_page = pdf_document[0]
            pix = first_page.get_pixmap()
            img_data = pix.tobytes("png")
            return base64.b64encode(img_data).decode("utf-8")
        return ""

    @abstractmethod
    def _download_obj(self, path: str) -> str:
        pass

    @abstractmethod
    def _list_directory(self, path: str) -> List[str]:
        pass

    @repo_error_handler
    def get_obj(self, path: str) -> str:
        if path.endswith("/"):
            return self._list_directory(path)
        elif path.endswith((".yaml", ".yml")):
            return self._get_yaml(path)
        elif path.endswith(".json"):
            return self._get_json(path)
        elif path.lower().endswith((".png", ".jpg", ".jpeg")):
            return self._get_image(path)
        elif path.lower().endswith(".pdf"):
            return self._get_pdf(path)
        elif path.lower().endswith(".txt"):
            return self._get_text(path)
        else:
            return self._get_binary(path)

    @repo_error_handler
    def download_obj(self, path: str) -> str:
        return self._download_obj(path)


class RepoException(AppException):
    pass
