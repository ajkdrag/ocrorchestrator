import pathlib
from contextlib import contextmanager
from typing import Any, Dict, List

from pydantic import BaseModel, Field, create_model

from ..config.app_config import FieldInfo


@contextmanager
def set_posix_windows():
    posix_backup = pathlib.PosixPath
    try:
        pathlib.PosixPath = pathlib.WindowsPath
        yield
    finally:
        pathlib.PosixPath = posix_backup


def generate_dynamic_model(
    fields: List[FieldInfo],
    name="ExtractedOutputModel",
) -> BaseModel:
    field_definitions = {}
    for field_info in fields:
        field = field_info.name
        desc = field_info.description
        if field.startswith("list_"):
            field_definitions[field] = (
                list, Field(default=[], description=desc))
        elif field.startswith("is_"):
            field_definitions[field] = (
                bool, Field(default=False, description=desc))
        elif field.startswith("num_"):
            field_definitions[field] = (
                int, Field(default=None, description=desc))
        elif field.endswith(("_no", "_date", "_name")):
            field_definitions[field] = (
                str, Field(default="", description=desc))
        elif field.endswith("amount"):
            field_definitions[field] = (
                float,
                Field(default=-999999999, description=desc),
            )
        elif field.endswith("amounts"):
            field_definitions[field] = (
                dict, Field(default={}, description=desc))
        else:
            field_definitions[field] = (
                str, Field(default="", description=desc))

    return create_model(name, **field_definitions)


def create_dynamic_message(
    resp: Dict[str, Any], fields: List[FieldInfo] = None
) -> BaseModel:
    if fields is None:
        field_definitions = {field: (type(value), ...)
                             for field, value in resp.items()}
    else:
        field_definitions = {
            field.name: (type(resp[field.name]), ...)
            for field in fields
            if field.name in resp
        }
    DynamicMessage = create_model("DynamicMessage", **field_definitions)
    return DynamicMessage(**resp)


def create_task_key(category, task):
    return f"{category}__{task}"