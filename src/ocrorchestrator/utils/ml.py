from typing import Optional

import structlog
import torch

from .constants import PRETRAINED_MODELS

log = structlog.get_logger()


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_pretrained_classifier(
    model_name,
    checkpoint=None,
    num_classes=None,
    device: Optional[torch.device] = None,
):
    if model_name not in PRETRAINED_MODELS:
        raise ValueError(f"Model {model_name} is not supported.")

    device = device or get_device()

    model = PRETRAINED_MODELS[model_name](weights="DEFAULT")

    if num_classes is not None:
        model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

    log.info(
        f"Initialized model {model_name} with {num_classes} classes, on {device}")
    if checkpoint:
        log.info(f"Loading from checkpoint: {checkpoint}")
        model.load_state_dict(torch.load(checkpoint, map_location=device))

    return model
