from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, create_model


def generate_dynamic_model(
    fields: List[str],
    name="ExtractedOutputModel",
) -> BaseModel:
    field_definitions = {}
    for field in fields:
        if field.startswith("is_"):
            field_definitions[field] = (bool, Field(default=False))
        elif field.endswith(("_no", "_date", "_name")):
            field_definitions[field] = (str, Field(default=""))
        elif field.endswith("amount"):
            field_definitions[field] = (float, Field(default=None))
        elif field.endswith("amounts"):
            field_definitions[field] = (dict, Field(default={}))
        else:
            field_definitions[field] = (str, Field(default=""))

    return create_model(name, **field_definitions)


def create_dynamic_message(
    resp: Dict[str, Any], fields: Optional[List[str]] = None
) -> BaseModel:
    if fields is None:
        field_definitions = {field: type(value)
                             for field, value in resp.items()}
    else:
        field_definitions = {
            field: type(resp[field]) for field in fields if field in resp
        }
    DynamicMessage = create_model("DynamicMessage", **field_definitions)
    return DynamicMessage(**resp)


def create_task_key(category, task):
    return f"{category}__{task}"
