import traceback
from typing import Callable

from fastapi import APIRouter, Depends

from .datamodels.api_io import AppException, AppResponse, OCRRequest
from .deps import get_processor
from .processors import BaseProcessor
from .utils.constants import ErrorCode
from .utils.misc import create_dynamic_message

ocr_router = APIRouter()


def process_request(req: OCRRequest, process_func: Callable) -> AppResponse:
    try:
        response = process_func(req)
        message = create_dynamic_message(response, req.fields)
        return AppResponse(status="OK", status_code=200, message=message)
    except Exception as e:
        if not isinstance(e, AppException):
            e = AppException(
                ErrorCode.INTERNAL_SERVER_ERROR,
                traceback.format_exc(),
            )
        raise e


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
