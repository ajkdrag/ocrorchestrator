import os
from typing import Dict

from ..artifacts import BaseArtifact
from ..config.app_config import AppConfig, OCRConfig
from ..repos.base import BaseRepo


class ArtifactManager:
    def __init__(
        self,
        repo: BaseRepo,
        config_path: str,
        local_artifact_dir: str = "./artifacts",
    ):
        self.repo = repo
        self.config_path = config_path
        self.local_artifact_dir = local_artifact_dir
        self.app_config = None
        self.artifacts: Dict[str, BaseArtifact] = {}
        self.prompts: Dict[str, str] = {}
        self.models: Dict[str, str] = {}
        self._initialize()

    def _initialize(self, lazy=True):
        config_dict = self.repo.get_yaml(self.config_path)
        self.app_config = AppConfig(OCRConfig(categories=config_dict))
        if not lazy:
            _ = [
                self.get_prompt(task_cfg.prompt_template)
                for _, _, task_cfg in self.app_config.iterate()
                if task_cfg.prompt_template is not None
            ]

            _ = [
                self.get_model_path(task_cfg.extra_kwargs["model"])
                for _, _, task_cfg in self.app_config.iterate()
                if "model" in task_cfg.extra_kwargs
            ]

    def get_config(self) -> AppConfig:
        return self.app_config

    def get_artifact(self, artifact_name: str, in_memory=True) -> str:
        if artifact_name not in self.artifacts:
            self.repo.download_artifact(artifact_name, self.local_artifact_dir)

    def get_prompt(self, prompt_name: str) -> str:
        if prompt_name not in self.artifacts:
            prompt_path = f"{self.app_config}/{prompt_name}"
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
    from ..repos.factory import RepoFactory

    repo = RepoFactory.create_repo("local", base_path="../../data")
    artifact_manager = ArtifactManager(repo, "../../artifacts", "config.yaml")

    app_config = artifact_manager.get_app_config()
    print(f"Config: {app_config}")

    prompt = artifact_manager.get_prompt("doc_validation_v1.txt")
    print(f"Prompt: {prompt[:50]}...")

    model_path = artifact_manager.get_model_path("pof_val_v1.pt")
    print(f"Model path: {model_path}")
