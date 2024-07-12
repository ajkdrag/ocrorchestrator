import os
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from uuid import uuid4

from pydantic import BaseModel, Field, root_validator

from ..utils.constants import ErrorCode


class ConfigUpdateRequest(BaseModel):
    config: Optional[Dict] = None
    config_file: Optional[str] = None


class SaveOptions(BaseModel):
    path: str
    format: str = "json"


class OCRRequest(BaseModel):
    image: str  # base64 image as utf-8
    guid: str = Field(default_factory=uuid4)
    category: str
    task: str
    fields: Optional[List[str]] = None
    save_options: Optional[SaveOptions] = None
    log_result: bool = True

    @staticmethod
    def from_offline_req(OCRRequestOffline, image):
        req_dict = OCRRequestOffline.dict()
        req_dict["image"] = image
        return OCRRequest(**req_dict)


class OCRRequestOffline(BaseModel):
    location: str  # path to gcs/s3/folder/file
    guid: str = Field(default_factory=uuid4)
    category: str
    task: str
    fields: Optional[List[str]] = None
    save_options: Optional[SaveOptions] = None
    log_result: bool = True

    @root_validator(pre=True)
    def validate_save_options_path(cls, values):
        save_options = values.get("save_options")
        if save_options and save_options.path:
            path = save_options.path

            # Check if the path looks like a file path
            _, ext = os.path.splitext(path)
            if ext:
                raise ValueError(
                    "save_options.path must be a directory path, not a file path"
                )

            save_options.path = save_options.path.rstrip("/") + "/"

        return values


class AppResponse(BaseModel):
    status: str
    status_code: int
    message: Any


class AppException(HTTPException):
    def __init__(self, error_code: ErrorCode, detail: str = None):
        super().__init__(
            status_code=error_code.status_code,
            detail=f"{error_code.name}: {detail or error_code.message}",
        )
        self.status = error_code.name


class AppException2(Exception):
    def __init__(self, error_code: ErrorCode, detail: str = None):
        super().__init__(
            *[
                error_code.status_code,
                f"{error_code.name}: {detail or error_code.message}",
            ]
        )
        self.status = error_code.name
        self.status_code = error_code.status_code
        self.detail = f"{error_code.name}: {detail or error_code.message}"
