from typing import Any, Dict

import structlog

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import OCRRequest
from ..repos import BaseRepo
from ..utils.img import get_image_mime_type
from ..utils.mixins import VertexAILangchainMixin
from .base import BaseProcessor

log = structlog.get_logger()


class LLMProcessor(BaseProcessor, VertexAILangchainMixin):
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        super().__init__(task_config, general_config, repo)
        self.prompts_dir = general_config.prompts_dir
        self.prompt_file = task_config.prompt_template
        self.model_name = task_config.model
        self.fields = task_config.fields
        self.model_config = {
            "temperature": task_config.kwargs.get("temperature", 0.1),
            "top_p": task_config.kwargs.get("top_p", 0.4),
            "top_k": task_config.kwargs.get("top_k", 28),
            "max_output_tokens": task_config.kwargs.get(
                "max_output_tokens",
                2048,
            ),
        }

    def _setup(self):
        self.template = self.repo.get_obj(
            f"{self.prompts_dir}/{self.prompt_file}")
        self.load_llm(model_name=self.model_name, **self.model_config)
        if self.fields:
            self.load_output_parser(self.fields)
            self.load_prompt(self.template)

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        image_data = f"data:{get_image_mime_type(req.image)};base64,{req.image}"
        if self.fields is None:
            self.load_output_parser(req.fields)
            self.load_prompt(self.template)
        return self.predict(image_data)
