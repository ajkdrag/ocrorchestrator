import traceback
from typing import Callable

import structlog
from fastapi import APIRouter, Depends

from .datamodels.api_io import (
    AppException,
    AppResponse,
    ConfigUpdateRequest,
    OCRRequest,
)
from .deps import get_processor, update_app_state
from .processors import BaseProcessor
from .utils.constants import ErrorCode
from .utils.misc import create_dynamic_message

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
async def predict(
    req: OCRRequest,
    processor: BaseProcessor = Depends(get_processor),
):
    return process_request(req, processor.process)


@ocr_router.post("/predict_offline")
async def predict_offline(
    req: OCRRequest,
    processor: BaseProcessor = Depends(get_processor),
):
    return process_request(req, processor.process_offline)


@ocr_router.post("/update_config")
async def update_config(
    config_update: ConfigUpdateRequest,
    update_state=Depends(update_app_state),
):
    if config_update.config:
        return process_request(config_update.config, update_state)
    elif config_update.config_file:
        return process_request(config_update.config_file, update_state)
    else:
        raise AppException(ErrorCode.BAD_REQUEST, "No valid config provided")
