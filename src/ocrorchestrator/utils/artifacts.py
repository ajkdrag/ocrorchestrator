import os

from ..config.app_config import AppConfig, OCRConfig
from .gcs import GCSUtils


class ArtifactManager:
    def __init__(
        self,
        repo: GCSUtils,
        config_path: str,
        local_artifact_dir: str = "./artifacts",
        prompt_templates_dir: str = "prompt_templates",
        models_dir: str = "models",
    ):
        self.repo = repo
        self.config_path = config_path
        self.local_artifact_dir = local_artifact_dir
        self.prompt_templates_dir = prompt_templates_dir
        self.models_dir = models_dir
        self.app_config = None
        self.prompts = {}
        self.models = {}
        self._initialize()

    def _initialize(self, lazy=True):
        config_dict = self.repo.get_yaml(self.config_path)
        self.app_config = AppConfig(OCRConfig(categories=config_dict))
        if not lazy:
            _ = [
                self.get_prompt(task_cfg.prompt_template)
                for cat, task, task_cfg in self.app_config.iterate()
                if task_cfg.prompt_template is not None
            ]

            _ = [
                self.get_model_path(task_cfg.extra_kwargs["model"])
                for cat, task, task_cfg in self.app_config.iterate()
                if "model" in task_cfg.extra_kwargs
            ]

    def get_config(self) -> AppConfig:
        return self.app_config

    def get_prompt(self, prompt_name: str) -> str:
        if prompt_name not in self.prompts:
            prompt_path = f"{self.prompt_templates_dir}/{prompt_name}"
            self.prompts[prompt_name] = self.repo.get_text(prompt_path)
        return self.prompts[prompt_name]

    def get_model_path(self, model_name: str) -> str:
        if model_name not in self.models:
            local_path = os.path.join(self.local_artifact_dir, model_name)
            self.repo.download_model(
                f"{self.models_dir}/{model_name}",
                local_path,
            )
        self.models[model_name] = local_path
        return self.models[model_name]

    def refresh(self):
        self.prompts.clear()
        self.models.clear()
        self._initialize()


if __name__ == "__main__":
    gcs = GCSUtils("canonical-ocr-bucket")
    artifact_manager = ArtifactManager(gcs, "./artifacts", "config.yaml")

    config = artifact_manager.get_config()
    print(f"Config: {config.get_config()}")

    prompt = artifact_manager.get_prompt("doc_validation_v1.txt")
    print(f"Prompt: {prompt[:50]}...")

    model_path = artifact_manager.get_model_path("pof_val_v1.pt")
    print(f"Model path: {model_path}")
