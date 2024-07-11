from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field

from ..utils.constants import ErrorCode


class ConfigUpdateRequest(BaseModel):
    config: Optional[Dict] = None
    config_file: Optional[str] = None


class SaveOptions(BaseModel):
    output_path: str
    output_format: str = "json"


class OCRRequest(BaseModel):
    image: str  # base64 image as utf-8
    guid: Optional[str] = Field(default_factory=uuid4)
    category: str
    task: str
    fields: Optional[List[str]] = None
    save_options: Optional[SaveOptions] = None


class OCRRequestOffline(BaseModel):
    location: str  # path to gcs/s3
    guid: Optional[str] = Field(default_factory=uuid4)
    category: str
    task: str
    fields: Optional[List[str]] = Field(default_factory=list)
    save_options: Optional[SaveOptions] = None


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
