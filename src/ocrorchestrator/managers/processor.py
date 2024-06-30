from typing import Dict

from ..config.app_config import AppConfig
from ..processors import BaseProcessor
from ..processors.factory import ProcessorFactory
from ..repos import BaseRepo
from ..utils.misc import create_task_key


class ProcessorManager:
    def __init__(self, app_config: AppConfig, repo: BaseRepo):
        self.app_config = app_config
        self.repo = repo
        self.processors: Dict[str, BaseProcessor] = {}
        self._initialize()

    def _initialize(self):
        for cat, task, task_config in self.app_config.iterate():
            key = create_task_key(cat, task)
            processor = ProcessorFactory.create_processor(
                task_config,
                self.app_config.general,
                self.repo,
            )
            processor.setup()
            self.processors[key] = processor

    def refresh(self):
        self.processors.clear()
        self._initialize()
