from ..config.app_config import GeneralConfig, TaskConfig
from ..processors import (
    BaseProcessor,
    DocumentValidationProcessor,  # noqa: F401
    LLMProcessor,
    MicroserviceProcessor,
)
from ..repos import BaseRepo


class ProcessorFactory:
    @staticmethod
    def create_processor(
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ) -> BaseProcessor:
        name = task_config.processor
        if name == "llm":
            return LLMProcessor(task_config, general_config, repo)
        elif name == "microservice":
            return MicroserviceProcessor(task_config, general_config, repo)
        elif name == "custom":
            class_name = task_config.handler
            return globals()[class_name](task_config, general_config, repo)
        else:
            raise ValueError(f"Unknown processor: {name}")
