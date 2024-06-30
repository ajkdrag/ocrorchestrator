from typing import Any, Dict

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import OCRRequest
from ..repos import BaseRepo
from .base import BaseProcessor


class DocumentValidationProcessor(BaseProcessor):
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        super().__init__(task_config, general_config, repo)
        self.models_dir = general_config.models_dir
        self.model_file = task_config.model

    def setup(self):
        # TODO: instantiate the pytorch model
        pass

    def process(self, req: OCRRequest) -> Dict[str, Any]:
        return {
            "is_valid": True,
        }
