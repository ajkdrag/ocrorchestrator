import functools
import traceback
from typing import Any, Callable, Dict

import structlog

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import (
    AppException,
    OCRRequest,
    OCRRequestOffline,
)
from ..repos import BaseRepo
from ..utils.constants import ErrorCode

log = structlog.get_logger()


def process_error_handler(func: Callable):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            error_code = (
                ErrorCode.PROCESS_CLEANUP_ERROR
                if func.__name__.startswith("cleanup")
                else ErrorCode.PROCESSING_ERROR
            )
            log.error(
                f"Process operation error in {func.__name__}",
                status_code=error_code.status_code,
                status=error_code.name,
                exc_info=True,
            )
            raise ProcessorException(error_code, traceback.format_exc()) from e

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
        self.log_model_output = general_config.log_model_output

    def _setup(self) -> None:
        raise NotImplementedError

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        raise NotImplementedError

    def _process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        raise NotImplementedError

    @process_error_handler
    def cleanup(self) -> None:
        pass

    @process_error_handler
    def process(self, req: OCRRequest) -> Dict[str, Any]:
        log.info("--- Processing online request ---")
        result = self._process(req)
        if self.log_model_output:
            log.info("Model output", output=result)
        return result

    @process_error_handler
    def process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        log.info("--- Processing offline request ---")
        result = self._process_offline(req)
        if self.log_model_output:
            log.info("Model output", output=result)
        return result


class ProcessorException(AppException):
    pass
