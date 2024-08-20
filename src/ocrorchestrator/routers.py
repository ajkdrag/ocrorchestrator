import time
import traceback
from typing import Callable, List, Union

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .config.app_config import AppConfig
from .datamodels.api_io import (
    AppException,
    AppResponse,
    ConfigUpdateRequest,
    OCRRequest,
    OCRRequestOffline,
)
from .deps import get_processor, proc_manager
from .processors import BaseProcessor
from .utils.constants import ErrorCode
from .utils.misc import create_dynamic_message
from .utils.timing import log_execution_time

ocr_router = APIRouter()
log = structlog.get_logger()
APP_NAME = "ocrorchestrator"


def process_request(req: BaseModel, func: Callable) -> AppResponse:
    try:
        start_time = time.time()
        response = func(req)

        if "fields" in req.model_fields and (
            req.fields is not None and req.save_options is None
        ):
            response = _format_response(response, req.fields)

        elapsed = (time.time() - start_time) * 1000
        log.info(f"Request processed successfully. Elapsed: {elapsed}")
        return AppResponse(
            status="OK",
            status_code=200,
            execution_time_millis=elapsed,
            message=response,
        )

    except AppException as ae:
        log.error("Application-specific exception occurred", exc_info=True)
        raise ae

    except Exception as e:
        error_code = ErrorCode.INTERNAL_SERVER_ERROR
        log.error(
            "Unexpected error occurred",
            error=str(e),
            function=func.__name__,
            status_code=error_code.status_code,
            status=error_code.name,
            exc_info=True,
        )
        raise AppException(error_code, traceback.format_exc())


def _format_response(
    response: Union[dict, List[dict]],
    fields: List[str],
) -> Union[dict, List[dict]]:
    if isinstance(response, list):
        return [create_dynamic_message(r, fields) for r in response]
    return create_dynamic_message(response, fields)


@ocr_router.post(f"/{APP_NAME}/predict")
@log_execution_time
async def predict(
    req: OCRRequest,
    processor: BaseProcessor = Depends(get_processor),
):
    return process_request(req, processor.process)


@ocr_router.post(f"/{APP_NAME}/predict_offline")
@log_execution_time
async def predict_offline(
    req: OCRRequestOffline,
    processor: BaseProcessor = Depends(get_processor),
):
    return process_request(req, processor.process_offline)


@ocr_router.post(f"/{APP_NAME}/update_config")
@log_execution_time
async def update_config(
    config_update: ConfigUpdateRequest,
):
    if config_update.config:
        new_config = AppConfig(**config_update.config)
        return process_request(new_config, proc_manager.refresh)
    elif config_update.config_file:
        new_config = AppConfig(
            **proc_manager.repo.get_obj(
                config_update.config_file,
            )
        )
        return process_request(new_config, proc_manager.refresh)
    else:
        raise AppException(ErrorCode.BAD_REQUEST, "No valid config provided")