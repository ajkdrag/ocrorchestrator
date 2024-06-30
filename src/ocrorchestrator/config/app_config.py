from collections import OrderedDict
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, root_validator


class TaskConfig(BaseModel):
    processor: str
    handler: Optional[str] = None
    model: Optional[str] = None
    prompt_template: Optional[str] = None
    extra_kwargs: Optional[Dict] = Field(default_factory=dict)
    fields: Optional[List[str]] = None
    classes: Optional[List[str]] = None


class GeneralConfig(BaseModel):
    prompts_dir: Optional[str] = Field(default="prompt_templates")
    models_dir: Optional[str] = Field(default="models")


class AppConfig(BaseModel):
    general: GeneralConfig
    categories: Dict[str, OrderedDict[str, Optional[TaskConfig]]]

    @root_validator(pre=True)
    def ensure_general_config(cls, values):
        if "general" not in values or values["general"] is None:
            values["general"] = GeneralConfig().dict()
        return values

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
            raise ValueError(f"Task '{task}' not found for category '{category}'")

        return task_config
