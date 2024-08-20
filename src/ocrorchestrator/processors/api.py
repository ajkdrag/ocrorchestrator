from string import Template
from typing import Any, Dict

import requests
import structlog

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import AppException, OCRRequest
from ..repos import BaseRepo
from ..utils.constants import ErrorCode
from .base import BaseProcessor

log = structlog.get_logger()


class InputFormatter:
    def __init__(self, format_template: Dict[str, Any]):
        self.format_template = format_template

    def format(self, data: Any) -> Dict[str, Any]:
        def _format_value(value):
            if isinstance(value, str):
                return Template(value).safe_substitute(data.__dict__)
            elif isinstance(value, dict):
                return {k: _format_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_format_value(item) for item in value]
            return value

        return _format_value(self.format_template)


class ApiProcessor(BaseProcessor):
    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        super().__init__(task_config, general_config, repo)
        self.api = task_config.api
        self.input_format = InputFormatter(task_config.kwargs)

    def _setup(self):
        self.client = requests.Session()

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        formatted_input = self.input_format.format(req)

        try:
            log.info("Sending API request", api_endpoint=self.api)
            response = self.client.post(self.api, json=formatted_input)
            response.raise_for_status()
            result = response.json()
            log.info(
                "API request successful",
                api_endpoint=self.api,
                status_code=response.status_code,
            )
        except requests.RequestException as e:
            error_code = ErrorCode.API_CALL_ERROR
            log.error(
                "API request failed",
                api_endpoint=self.api,
                status_code=error_code.status_code,
                status=error_code.name,
                exc_info=True,
            )
            raise AppException(error_code,
                               f"API call error: {str(e)}")

        return self._result_parser(result)

    def _result_parser(self, raw: Any) -> Dict[str, Any]:
        return raw

    def cleanup(self):
        self.client.close()