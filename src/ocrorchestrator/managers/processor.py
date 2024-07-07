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
        log.info("**** Initializing processors ****")
        for cat, task, task_config in self.app_config.iterate():
            key = create_task_key(cat, task)
            processor = ProcessorFactory.create_processor(
                task_config,
                self.app_config.general,
                self.repo,
            )
            log.info("Setting up processor",
                     processor=type(processor).__name__)
            processor._setup()
            self.processors[key] = processor
        log.info("**** Processors initialized ****")

    def refresh(self, new_config: AppConfig = None):
        log.info("**** Refreshing processors ****")
        self.cleanup()
        self.processors.clear()
        if new_config:
            self.app_config = new_config
        self._initialize()
        return self.app_config

    def cleanup(self):
        log.info("**** Cleaning up processors ****")
        for key, processor in self.processors.items():
            try:
                processor.cleanup()
            except Exception:
                log.error(
                    "Error during processor cleanup",
                    processor_key=key,
                    processor_type=type(processor).__name__,
                    exc_info=True,
                )
