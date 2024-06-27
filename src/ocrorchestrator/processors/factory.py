from typing import Dict

from ..processors import (
    BaseProcessor,
    LLMProcessor,
    MicroserviceProcessor,
)
from ..utils.artifacts import ArtifactManager


class ProcessorFactory:
    def __init__(self, artifact_manager: ArtifactManager):
        self.artifact_manager = artifact_manager
        self.processors: Dict[str, BaseProcessor] = {}
        self._initialize()

    def _initialize(self):
        app_config = self.artifact_manager.get_config()
        for category, task_type, task_config in app_config.iterate():
            key = f"{category}_{task_type}"
            if task_config.processor == "llm":
                self.processors[key] = LLMProcessor(
                    task_config, self.artifact_manager)
            elif task_config.processor == "microservice":
                self.processors[key] = MicroserviceProcessor(
                    task_config, self.artifact_manager
                )
            elif task_config.processor == "custom":
                self.processors[key] = globals()[task_config.handler](
                    task_config, self.artifact_manager
                )
            else:
                raise ValueError(f"Unknown processor: {task_config.processor}")

    def refresh(self):
        self.processors.clear()
        self._initialize()
