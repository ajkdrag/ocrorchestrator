def get_device():
    import torch

    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_pretrained_classifier(
    model_name, checkpoint=None, num_classes=None, device="cpu"
):
    import torch
    import torchvision.models as models
    from torchvision.models import ResNet18_Weights, ResNet50_Weights

    available_models = {
        "resnet50": (models.resnet50, ResNet50_Weights.IMAGENET1K_V1),
        "resnet18": (models.resnet18, ResNet18_Weights.IMAGENET1K_V1),
        "efficientnet_b0": (models.efficientnet_b0,),
        "efficientnet_b3": (models.efficientnet_b3,),
        "vit_b_16": (models.vit_b_16,),
    }

    if model_name not in available_models:
        raise ValueError(f"Model {model_name[0]} is not supported.")

    model_cls, weights = available_models[model_name]
    model = model_cls(weights=weights)

    if num_classes is not None:
        if isinstance(model, models.ResNet):
            model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
        elif isinstance(model, models.EfficientNet):
            model.classifier = torch.nn.Linear(
                model.classifier[1].in_features, num_classes
            )
        elif isinstance(model, models.VisionTransformer):
            model.heads = torch.nn.Linear(model.heads.in_features, num_classes)
        else:
            raise ValueError(
                f"Unsupported model architecture for {model_name}")

    if checkpoint:
        print("Loading from checkpoint", checkpoint)
        model.load_state_dict(torch.load(checkpoint, map_location=device))

    return model
