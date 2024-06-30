from typing import Any, Dict, List, Optional

from pydantic import BaseModel, create_model


def create_dynamic_message(
    resp: Dict[str, Any], fields: Optional[List[str]] = None
) -> BaseModel:
    if fields is None:
        field_definitions = {field: (type(value), ...) for field, value in resp.items()}
    else:
        field_definitions = {field: (Any, ...) for field in fields if field in resp}
    DynamicMessage = create_model("DynamicMessage", **field_definitions)
    return DynamicMessage(**resp)


def create_task_key(category, task):
    return f"{category}__{task}"
