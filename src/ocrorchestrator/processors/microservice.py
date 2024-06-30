from typing import Any, Dict

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import OCRRequest
from ..repos import BaseRepo
from .base import BaseProcessor


class MicroserviceProcessor(BaseProcessor):
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        super().__init__(task_config, general_config, repo)
        self.url = task_config.handler

    def setup(self):
        pass

    def process(self, req: OCRRequest) -> Dict[str, Any]:
        raise NotImplementedError
