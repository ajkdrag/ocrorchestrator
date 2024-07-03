from typing import Dict

import structlog

from ..config.app_config import AppConfig
from ..processors import BaseProcessor
from ..processors.factory import ProcessorFactory
from ..repos import BaseRepo
from ..utils.misc import create_task_key

log = structlog.get_logger()


class ProcessorManager:
    def __init__(self, app_config: AppConfig, repo: BaseRepo):
        self.app_config = app_config
        self.repo = repo
        self.processors: Dict[str, BaseProcessor] = {}
        self._initialize()

    def _initialize(self):
        log.info("++++ Initializing processors ++++")
        for cat, task, task_config in self.app_config.iterate():
            key = create_task_key(cat, task)
            processor = ProcessorFactory.create_processor(
                task_config,
                self.app_config.general,
                self.repo,
            )
            log.info(f"Setting up processor: {processor.__class__.__name__}")
            processor._setup()
            self.processors[key] = processor
        log.info("++++ Processors initialized ++++")

    def refresh(self):
        log.info("++++ Refreshing processors ++++")
        self.processors.clear()
        self._initialize()
