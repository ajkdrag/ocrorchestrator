from string import Template
from typing import Any, Dict

import requests

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import AppException, OCRRequest
from ..repos import BaseRepo
from ..utils.constants import ErrorCode
from .base import BaseProcessor


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
        # Format the input according to the template
        formatted_input = self.input_format.format(req)

        try:
            response = self.client.post(self.api, json=formatted_input)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            raise AppException(ErrorCode.API_CALL_ERROR,
                               f"API call error: {str(e)}")

        return self._result_parser(result)

    def _result_parser(self, raw: Any) -> Dict[str, Any]:
        return raw

    def cleanup(self):
        self.client.close()
