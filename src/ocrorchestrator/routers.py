import traceback
from typing import Callable

import structlog
from fastapi import APIRouter, Depends

from .config.app_config import AppConfig
from .datamodels.api_io import (
    AppException,
    AppResponse,
    ConfigUpdateRequest,
    OCRRequest,
)
from .deps import get_proc_manager, get_processor
from .managers.processor import ProcessorManager
from .processors import BaseProcessor
from .utils.constants import ErrorCode
from .utils.misc import create_dynamic_message
from .utils.timing import log_execution_time

ocr_router = APIRouter()
log = structlog.get_logger()


def process_request(req: OCRRequest, func: Callable) -> AppResponse:
    try:
        response = func(req)
        if hasattr(req, "fields"):
            response = create_dynamic_message(response, req.fields)
        log.info("--- Request processed successfully ---")
        return AppResponse(status="OK", status_code=200, message=response)
    except Exception as e:
        if isinstance(e, AppException):
            raise e

        error_code = ErrorCode.INTERNAL_SERVER_ERROR
        log.error(
            f"Error in {func.__name__}",
            status_code=error_code.status_code,
            status=error_code.name,
            exc_info=True,
        )

        raise AppException(error_code, traceback.format_exc()) from e


@ocr_router.post("/predict")
@log_execution_time
async def predict(
    req: OCRRequest,
    processor: BaseProcessor = Depends(get_processor),
):
    return process_request(req, processor.process)


@ocr_router.post("/predict_offline")
@log_execution_time
async def predict_offline(
    req: OCRRequest,
    processor: BaseProcessor = Depends(get_processor),
):
    return process_request(req, processor.process_offline)


@ocr_router.post("/update_config")
@log_execution_time
async def update_config(
    config_update: ConfigUpdateRequest,
    manager: ProcessorManager = Depends(get_proc_manager),
):
    if config_update.config:
        new_config = AppConfig(**config_update.config)
        return process_request(new_config, manager.refresh)
    elif config_update.config_file:
        new_config = AppConfig(
            **manager.repo.get_obj(
                config_update.config_file,
            )
        )
        return process_request(new_config, manager.refresh)
    else:
        raise AppException(ErrorCode.BAD_REQUEST, "No valid config provided")
