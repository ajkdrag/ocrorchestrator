from collections import OrderedDict
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator


class TorchClassifierOutput(BaseModel):
    prediction: str
    conf: float
    probs: Dict[str, float]


class TaskConfig(BaseModel):
    processor: str
    api: Optional[str] = None
    model: Optional[str] = None
    prompt_template: Optional[str] = None
    params: List = Field(default_factory=list)
    fields: Optional[List[str]] = None
    classes: Optional[List[str]] = None
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def extract_args_and_kwargs(cls, values):
        params = values.get("params", [])
        args = []
        kwargs = {}
        for param in params:
            if isinstance(param, dict):
                kwargs.update(param)
            else:
                args.append(param)
        values["args"] = args
        values["kwargs"] = kwargs
        return values


class GeneralConfig(BaseModel):
    prompts_dir: str = Field(default="prompts")
    models_dir: str = Field(default="models")
    normalization_stats: Dict[str, List[float]] = Field(
        default={
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225],
        }
    )


class AppConfig(BaseModel):
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    categories: Dict[str, OrderedDict[str, Optional[TaskConfig]]]

    def iterate(self) -> tuple[str, str, TaskConfig]:
        for category, category_config in self.categories.items():
            for task_type, task_config in category_config.items():
                if task_config is not None:
                    yield category, task_type, task_config

    def get_task_config(self, category: str, task: str) -> TaskConfig:
        category_config = self.categories.get(category)
        if not category_config:
            raise ValueError(f"Category '{category}' not found.")

        task_config = category_config.get(task)
        if not task_config:
            raise ValueError(
                f"Task '{task}' not found for category '{category}'")

        return task_config
