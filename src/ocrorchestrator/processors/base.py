from typing import Any, Dict

from ..config.app_config import TaskConfig
from ..utils.artifacts import ArtifactManager


class BaseProcessor:
    def __init__(
        self,
        task_config: TaskConfig,
        artifact_manager: ArtifactManager,
    ):
        self.task_config = task_config
        self.artifact_manager = artifact_manager

    async def process(self, image: bytes) -> Dict[str, Any]:
        raise NotImplementedError
