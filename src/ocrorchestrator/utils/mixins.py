from typing import Any

import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image

from ..config.app_config import TorchClassifierOutput
from .ml import get_device, load_pretrained_classifier


class TorchClassifierMixin:
    model: Any
    tfms: Any

    def load_model(
        self,
        model_name,
        checkpoint,
        class_names,
    ):
        self.device = get_device()
        self.model = load_pretrained_classifier(
            model_name,
            checkpoint,
            len(class_names),
            self.device,
        )
        self.model.to(self.device)
        self.model.eval()

    def load_tfms(self, img_size, norm_stats):
        self.tfms = transforms.Compose(
            [
                transforms.Resize(img_size),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=norm_stats["mean"],
                    std=norm_stats["std"],
                ),
            ]
        )

    def predict(
        self,
        image: Image.Image,
        class_names: list,
    ) -> TorchClassifierOutput:
        with torch.no_grad():
            img_tensor = self.tfms(image).unsqueeze(0).to(self.device)
            outputs = self.model(img_tensor).detach().cpu()
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            return TorchClassifierOutput(
                prediction=class_names[predicted.item()],
                conf=confidence.item(),
                probs={
                    class_names[i]: prob.item()
                    for i, prob in enumerate(probabilities[0])
                },
            )
