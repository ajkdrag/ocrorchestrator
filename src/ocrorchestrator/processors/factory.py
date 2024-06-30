from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import AppException
from ..processors import *  # noqa: F403
from ..processors.base import BaseProcessor
from ..repos import BaseRepo
from ..utils.constants import ErrorCode


class ProcessorFactory:
    @staticmethod
    def create_processor(
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ) -> BaseProcessor:
        class_name = task_config.processor
        try:
            return globals()[class_name](task_config, general_config, repo)
        except Exception as e:
            raise AppException(
                ErrorCode.INITIALIZATION_ERROR,
                f"Unknown processor: {class_name}. Exc: {e}",
            ) from e
