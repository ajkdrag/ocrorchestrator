import os
from typing import Union

import structlog
from fastapi import Request

from .config.app_config import AppConfig
from .datamodels.api_io import (
    AppException,
    OCRRequest,
    OCRRequestOffline,
)
from .managers.processor import ProcessorManager
from .managers.secrets import setup_google_credentials
from .processors import BaseProcessor
from .repos.factory import RepoFactory
from .utils.constants import ErrorCode
from .utils.misc import create_task_key

config_path = os.environ["CONFIG_PATH"]

log = structlog.get_logger()
log.info(f"Using starter config: {config_path}")

setup_google_credentials()

repo, content = RepoFactory.from_uri(config_path)
config = AppConfig(**content)
proc_manager = ProcessorManager(config, repo)


def get_proc_manager(req: Request) -> ProcessorManager:
    return req.app.state.proc_manager


def get_processor(
    req: Union[OCRRequest, OCRRequestOffline],
) -> BaseProcessor:
    key = create_task_key(req.category, req.task)
    processor = proc_manager.processors.get(key)
    if not processor:
        raise AppException(
            ErrorCode.PROCESSOR_NOT_FOUND,
            f"No processor found for {key}",
        )
    return processor