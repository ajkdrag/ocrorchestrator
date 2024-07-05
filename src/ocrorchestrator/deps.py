from typing import Union

from fastapi import Depends, Request

from .config.app_config import AppConfig
from .datamodels.api_io import AppException, OCRRequest
from .managers.processor import ProcessorManager
from .processors import BaseProcessor
from .repos import BaseRepo
from .utils.constants import ErrorCode
from .utils.misc import create_task_key


def get_repo(req: Request) -> BaseRepo:
    return req.app.state.repo


def get_config(req: Request) -> AppConfig:
    return req.app.state.config


def get_proc_manager(req: Request) -> ProcessorManager:
    return req.app.state.proc_manager


def get_processor(
    req: OCRRequest,
    manager: ProcessorManager = Depends(get_proc_manager),
) -> BaseProcessor:
    key = create_task_key(req.category, req.task)
    processor = manager.processors.get(key)
    if not processor:
        raise AppException(
            ErrorCode.PROCESSOR_NOT_FOUND,
            f"No processor found for {key}",
        )
    return processor


def update_app_state(
    req: Request,
    config: Union[str, dict] = None,
):
    if isinstance(config, dict):
        new_config = AppConfig(**config)
    elif isinstance(config, str):
        new_config = AppConfig(**req.app.state.repo.get_obj(config))
    else:
        raise AppException(ErrorCode.BAD_REQUEST, "Invalid config provided")

    req.app.state.config = new_config
    req.app.state.proc_manager.refresh(new_config)
    return new_config
