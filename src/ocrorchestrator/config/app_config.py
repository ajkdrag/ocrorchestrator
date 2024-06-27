from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TaskConfig(BaseModel):
    processor: str
    handler: str
    extra_kwargs: Optional[Dict] = Field(default_factory=dict)
    prompt_template: Optional[str] = None
    invalid: Optional[List[str]] = None
    fields: Optional[List[str]] = None
    classes: Optional[List[str]] = None


class CategoryConfig(BaseModel):
    validation: Optional[TaskConfig] = None
    classification: Optional[TaskConfig] = None
    extraction: Optional[TaskConfig] = None


class OCRConfig(BaseModel):
    categories: Dict[str, CategoryConfig]


class AppConfig:
    def __init__(self, config: OCRConfig):
        self._config = config

    def get_config(self) -> OCRConfig:
        return self._config

    def iterate(self) -> tuple[str, str, TaskConfig]:
        for category, category_config in self._config.categories.items():
            for task_type, task_config in category_config.items():
                if task_config is not None:
                    yield category, task_type, task_config

    def get_task_config(self, category: str, task_type: str) -> TaskConfig:
        category_config = self._config.categories.get(category)
        if not category_config:
            raise ValueError(
                f"Category '{category}' not found in configuration")

        task_config = getattr(category_config, task_type, None)
        if not task_config:
            raise ValueError(
                f"Task type '{task_type}' not found for category '{category}'"
            )

        return task_config

    def refresh(self, new_config: OCRConfig):
        self._config = new_config
