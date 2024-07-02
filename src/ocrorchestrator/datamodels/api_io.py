from typing import Any, List, Optional
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field, root_validator

from ..utils.constants import ErrorCode


class OCRRequest(BaseModel):
    image: str # base64 encoded image
    guid: Optional[str] = Field(default_factory=uuid4)
    category: str
    task: str
    fields: Optional[List[str]] = None

    @root_validator(pre=True)
    def image_to_utf8(cls, values):
        values["image"] = values["image"].decode("utf-8")
        return values


class OCRRequestOffline(BaseModel):
    location: str  # path to gcs/s3
    guid: Optional[str] = Field(default_factory=uuid4)
    category: str
    task: str
    fields: Optional[List[str]] = Field(default_factory=list)


class AppResponse(BaseModel):
    status: str
    status_code: int
    message: Any


class AppException(HTTPException):
    def __init__(self, error_code: ErrorCode, detail: str = None):
        super().__init__(
            status_code=error_code.status_code,
            detail=detail or error_code.message,
        )
        self.status = error_code.name
