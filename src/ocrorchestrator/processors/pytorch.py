import os
from typing import Any, Dict

from ..config.app_config import (
    GeneralConfig,
    TaskConfig,
)
from ..datamodels.api_io import OCRRequest
from ..repos import BaseRepo
from ..utils.constants import IMG_SIZE
from ..utils.img import base64_to_pil
from ..utils.mixins import TorchClassifierMixin
from .base import BaseProcessor


class DocumentValidationProcessor(BaseProcessor, TorchClassifierMixin):
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        super().__init__(task_config, general_config, repo)
        self.models_dir = general_config.models_dir
        self.model_name = task_config.model.split("__")[0]
        self.classes = self.task_config.classes

    def _setup(self):
        checkpoint = self.repo.download_obj(
            os.path.join(
                self.models_dir,
                self.task_config.model,
            )
        )
        self.load_model(
            self.model_name,
            checkpoint,
            self.classes,
        )

        self.load_tfms(
            self.task_config.kwargs.get("img_size", IMG_SIZE),
            self.general_config.normalization_stats,
        )

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        image = base64_to_pil(req.image)
        op = self.predict(image, self.task_config.classes)
        target = self.task_config.kwargs.get("target", self.classes[0])
        is_valid = op.prediction == target
        return {
            "is_valid": is_valid,
            "reason": op.prediction if not is_valid else None,
            "confidence": op.conf,
        }
