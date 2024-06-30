from typing import Any, Dict

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import OCRRequest, OCRRequestOffline
from ..repos import BaseRepo


class BaseProcessor:
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        self.task_config = task_config
        self.general_config = general_config
        self.repo = repo

    def setup(self) -> None:
        raise NotImplementedError

    def process(self, req: OCRRequest) -> Dict[str, Any]:
        raise NotImplementedError

    def process_offline(self, req: OCRRequestOffline) -> Dict[str, Any]:
        raise NotImplementedError
