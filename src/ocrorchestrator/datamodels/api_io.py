import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import HTTPException
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from typing_extensions import Self

from ..utils.constants import ErrorCode


class FieldInfo(BaseModel):
    name: str
    description: str = ""


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
    fields: Optional[List[FieldInfo]] = None
    save_options: Optional[SaveOptions] = None
    log_result: bool = True

    @field_validator("fields", mode="before")
    @classmethod
    def convert_fields_to_fieldinfo(cls, v: list) -> list:
        if v is None:
            return v
        return [
            FieldInfo(name=field) if isinstance(field, str) else field for field in v
        ]

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
    fields: Optional[List[FieldInfo]] = None
    save_options: Optional[SaveOptions] = None
    log_result: bool = True

    @field_validator("fields", mode="before")
    @classmethod
    def convert_fields_to_fieldinfo(cls, v: list) -> list:
        if v is None:
            return v
        return [
            FieldInfo(name=field) if isinstance(field, str) else field for field in v
        ]

    @model_validator(mode="after")
    def check_save_options(self) -> Self:
        if self.save_options is None:
            return self
        pth = self.save_options.path
        _, ext = os.path.splitext(pth)
        if ext:
            raise ValueError(
                "save_options.path must be a directory path, not a file path"
            )
        self.save_options.path = pth.rstrip("/") + "/"
        return self


class AppResponse(BaseModel):
    status: str
    status_code: int
    message: Any
    execution_time_millis: float = 0.0


class AppException(HTTPException):
    def __init__(self, error_code: ErrorCode, detail: str = None):
        super().__init__(
            status_code=error_code.status_code,
            detail=f"{error_code.name}: {detail or error_code.message}",
        )
        self.status = error_code.name