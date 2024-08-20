import os
from typing import Any, Dict

import numpy as np
import structlog
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from fastai.vision.all import load_learner
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import ChatVertexAI
from PIL import Image

from ..config.app_config import ClassifierOutput, FieldInfo
from .misc import generate_dynamic_model, set_posix_windows
from .ml import get_device, load_pretrained_classifier

log = structlog.get_logger()


class VertexAILangchainMixin:
    model: Any
    prompt_temp: Any
    output_parser: Any

    def load_llm(
        self,
        model_name: str,
        temperature: float,
        top_p: float,
        top_k: int,
        max_output_tokens: int,
    ):
        log.info("Loading Vertex AI LLM", model_name=model_name)
        self.model = ChatVertexAI(
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
            # safety_settings=SAFETY_SETTINGS,
        )

    def load_output_parser(self, fields: list[FieldInfo]):
        log.info("Loading output parser", fields=fields)
        ExtractedOutputModel = generate_dynamic_model(fields)
        self.output_parser = PydanticOutputParser(
            pydantic_object=ExtractedOutputModel,
        )

    def load_prompt(self, template: str):
        log.info("Loading prompt template")
        self.prompt_temp = PromptTemplate(
            template=template,
            input_variables=[],
            partial_variables={
                "format": self.output_parser.get_format_instructions(),
            },
        ).format()
        log.info("Prompt template loaded", template=self.prompt_temp)

    def predict(self, image_data: str) -> Dict[str, Any]:
        image_message = {
            "type": "image_url",
            "image_url": {"url": image_data},
        }
        text_message = {
            "type": "text",
            "text": self.prompt_temp,
        }
        message = HumanMessage(content=[image_message, text_message])
        result = self.model.invoke([message])
        log.info(
            "Raw LLM prediction completed successfully",
            result_preview=result.content[:100] + "...",
        )
        parsed = self.output_parser.parse(result.content)
        return parsed.dict()


class FastaiLearnerMixin:
    model: Any

    def load_model(
        self,
        model_name,
        checkpoint,
        warmup=True,
    ):
        is_windows = os.environ.get("APP_PLATFORM") == "windows"
        if is_windows:
            with set_posix_windows():
                learner = load_learner(checkpoint)
        else:
            learner = load_learner(checkpoint)

        log.info("Successfully loaded validation model")
        if warmup:
            log.info("Warming up the model ...")
            _ = learner.predict(
                np.random.uniform(
                    0,
                    255,
                    (224, 224, 3),
                ).astype(np.uint8)
            )
        self.model = learner

    def load_tfms(self, img_size, norm_stats):
        log.info("Loading image transformations", img_size=img_size)
        self.tfms = transforms.Compose(
            [
                transforms.Resize(img_size),
            ]
        )

    def predict(
        self,
        image: Image.Image,
        class_names: list,
    ) -> ClassifierOutput:
        preds = self.model.predict(image)
        result = ClassifierOutput(
            prediction=preds[0],
            conf=preds[2][preds[1].item()],
            probs={class_names[i]: prob.item()
                   for i, prob in enumerate(preds[2])},
        )
        log.info(
            "Classifier prediction completed",
            prediction=result.prediction,
            confidence=result.conf,
        )
        return result


class TorchClassifierMixin:
    model: Any
    tfms: Any

    def load_model(
        self,
        model_name,
        checkpoint,
        class_names,
    ):
        log.info("Loading PyTorch classifier", model_name=model_name)
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
        log.info("Loading image transformations", img_size=img_size)
        self.tfms = transforms.Compose(
            [
                transforms.Resize(img_size),
                transforms.ToTensor(),
                # transforms.Normalize(
                #     mean=norm_stats["mean"],
                #     std=norm_stats["std"],
                # ),
            ]
        )

    def predict(
        self,
        image: Image.Image,
        class_names: list,
    ) -> ClassifierOutput:
        with torch.no_grad():
            img_tensor = self.tfms(image).unsqueeze(0).to(self.device)
            outputs = self.model(img_tensor).detach().cpu()
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            result = ClassifierOutput(
                prediction=class_names[predicted.item()],
                conf=confidence.item(),
                probs={
                    class_names[i]: prob.item()
                    for i, prob in enumerate(probabilities[0])
                },
            )
        log.info(
            "PyTorch classifier prediction completed",
            prediction=result.prediction,
            confidence=result.conf,
        )
        return result