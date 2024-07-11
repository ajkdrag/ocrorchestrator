import functools
import json
import os
import traceback
from pathlib import Path
from typing import Any, Callable, Dict

import structlog

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import (
    AppException,
    OCRRequest,
    OCRRequestOffline,
    SaveOptions,
)
from ..repos import BaseRepo
from ..repos.factory import RepoFactory
from ..utils.constants import ErrorCode
from ..utils.timing import log_execution_time

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

    def _save_output(
        self,
        result: Dict[str, Any],
        save_options: SaveOptions,
        filename: str,
    ) -> str:
        if not self.output_repo:
            self.output_repo = self._get_repo(save_options.output_path)

        file_content = json.dumps(result)
        fname = f"{filename}.{save_options.output_format}"
        dir = save_options.output_path
        file_path = f"{dir}/{fname}"
        self.output_repo.save_file(file_path, file_content)
        return file_path

    def _process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        raise NotImplementedError

    @process_error_handler
    @log_execution_time
    def cleanup(self) -> None:
        pass

    @process_error_handler
    @log_execution_time
    def process(self, req: OCRRequest) -> Dict[str, Any]:
        log.info("--- Processing online request ---")
        result = self._process(req)
        if self.log_model_output:
            log.info("Model output", output=result)
        if req.save_options:
            saved_path = self._save_output(
                result,
                req.save_options,
                req.guid,
            )
            return {"saved_location": saved_path}
        return result

    @process_error_handler
    @log_execution_time
    def process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        log.info("--- Processing offline request ---")
        # TODO: build src repo from req.location
        src_repo = RepoFactory.from_uri(req.location)
        # TODO: build tgt repo from req.save_options.output_path
        result = self._process_offline(req)
        if self.log_model_output:
            log.info("Model output", output=result)
        return result


class ProcessorException(AppException):
    pass
