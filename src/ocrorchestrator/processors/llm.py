from typing import Any, Dict

import structlog

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import OCRRequest
from ..repos import BaseRepo
from .base import BaseProcessor

log = structlog.get_logger()


class LLMProcessor(BaseProcessor):
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        super().__init__(task_config, general_config, repo)
        self.prompts_dir = general_config.prompts_dir
        self.prompt_file = task_config.prompt_template
        self.model = task_config.model

    def setup(self):
        # TODO: instantiate langchain object
        log.info("Running LLM setup")
        pass

    def process(self, req: OCRRequest) -> Dict[str, Any]:
        log.info("Running LLM processor")
        return {
            "name": "John Doe",
            "invoice_no": "XYZ123",
        }
