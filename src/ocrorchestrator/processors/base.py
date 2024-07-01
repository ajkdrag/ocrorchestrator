import functools
import traceback
from typing import Any, Callable, Dict

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import (
    AppException,
    OCRRequest,
    OCRRequestOffline,
)
from ..repos import BaseRepo
from ..utils.constants import ErrorCode


def process_error_handler(func: Callable):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            error_code = ErrorCode.PROCESSING_ERROR
            raise AppException(error_code, traceback.format_exc()) from e

    return wrapper


class BaseProcessor:
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        self.task_config = task_config
        self.general_config = general_config
        self.repo = repo

    def _setup(self) -> None:
        raise NotImplementedError

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        raise NotImplementedError

    def _process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        raise NotImplementedError

    @process_error_handler
    def process(self, req: OCRRequest) -> Dict[str, Any]:
        return self._process(req)

    @process_error_handler
    def process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        return self._process_offline(req)
