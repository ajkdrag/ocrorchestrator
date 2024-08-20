from tempfile import NamedTemporaryFile
from typing import Any, Dict

from ..config.app_config import GeneralConfig, TaskConfig
from ..datamodels.api_io import OCRRequest
from ..repos import BaseRepo
from ..utils.img import base64_to_pil
from .base import BaseProcessor


class GradioProcessor(BaseProcessor):
    client: Any

    def __init__(
        self,
        task_config: TaskConfig,
        general_config: GeneralConfig,
        repo: BaseRepo,
    ):
        super().__init__(task_config, general_config, repo)
        self.api = task_config.api
        self.model = task_config.model

    def _setup(self):
        from gradio_client import Client

        self.client = Client(self.model)

    def _result_parser(self, raw: Any) -> Dict[str, Any]:
        return raw

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        from gradio_client import file

        image = base64_to_pil(req.image)

        with NamedTemporaryFile(delete=True, suffix=".jpg") as fp:
            image.save(fp.name)
            result = self.client.predict(
                file(fp.name),
                *self.task_config.args,
                api_name=self.api,
                **self.task_config.kwargs,
            )

            return self._result_parser(result)


class PaliGemmaGradioProcessor(GradioProcessor):
    def _result_parser(self, raw: Any) -> Dict[str, Any]:
        try:
            return {"output": raw[0]["value"][0]["token"]}
        except Exception as e:
            return {"error": str(e)}