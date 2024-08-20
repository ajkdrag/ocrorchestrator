import functools
import json
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
            raise ProcessorException(error_code, traceback.format_exc())

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

    def _save_output(
        self,
        result: Dict[str, Any],
        save_options: SaveOptions,
        repo: BaseRepo,
    ) -> str:
        file_content = json.dumps(result)
        return repo.save_file(save_options.path, file_content)

    @process_error_handler
    @log_execution_time
    def cleanup(self) -> None:
        pass

    @process_error_handler
    @log_execution_time
    def process(self, req: OCRRequest) -> Dict[str, Any]:
        log.info("--- Processing online request ---")
        result = self._process(req)
        if req.log_result:
            log.info("Model output", output=result)
        if req.save_options:
            opts = req.save_options
            repo, prefix = RepoFactory.from_uri(
                opts.path,
                read_prefix=False,
            )
            opts.path = prefix
            if opts.path.endswith("/"):
                opts.path += f"{req.guid}.{opts.format}"

            saved_path = self._save_output(result, opts, repo)
            return {"saved_location": saved_path}
        return result

    @process_error_handler
    @log_execution_time
    def process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        log.info("--- Processing offline request ---")
        src_repo, files_or_data = RepoFactory.from_uri(req.location)
        if isinstance(files_or_data, list):
            results = []
            for file_ in files_or_data:
                data = src_repo.get_obj(file_)
                subreq = OCRRequest.from_offline_req(
                    req,
                    data,
                )
                if subreq.save_options:
                    subreq.guid = Path(file_).stem

                results.append(self.process(subreq))

            if req.save_options:
                return {"saved_count": len(results)}
            else:
                return results

        else:
            subreq = OCRRequest.from_offline_req(
                req,
                files_or_data,
            )
            return self.process(subreq)


class ProcessorException(AppException):
    pass