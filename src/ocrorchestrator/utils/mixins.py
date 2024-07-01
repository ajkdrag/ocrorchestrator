from pathlib import Path
from typing import Any, Dict

import structlog
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import ChatVertexAI
from PIL import Image

from ..config.app_config import TorchClassifierOutput
from ..datamodels.api_io import AppException
from .constants import SAFETY_SETTINGS, ErrorCode
from .misc import generate_dynamic_model
from .ml import get_device, load_pretrained_classifier

log = structlog.get_logger()


class VertexAILangchainMixin:
    model: Any
    prompt: Any
    output_parser: Any

    def load_llm(
        self,
        model_name: str,
        temperature: float,
        top_p: float,
        top_k: int,
        max_output_tokens: int,
    ):
        self.model = ChatVertexAI(
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
            safety_settings=SAFETY_SETTINGS,
        )

    def load_output_parser(self, fields: list[str]):
        ExtractedOutputModel = generate_dynamic_model(fields)
        self.output_parser = PydanticOutputParser(
            pydantic_object=ExtractedOutputModel)

    def load_prompt(self, prompt: str):
        self.prompt = prompt
        self.prompt_temp = PromptTemplate(
            template="{sys_prompt}\n{format}\n",
            input_variables=[],
            partial_variables={
                "sys_prompt": prompt,
                "format": self.output_parser.get_format_instructions(),
            },
        )

    def predict(self, image_data: str) -> Dict[str, Any]:
        image_message = {
            "type": "image_url",
            "image_url": {"url": image_data},
        }
        text_message = {
            "type": "text",
            "text": self.prompt_temp.format(),
        }
        message = HumanMessage(content=[image_message, text_message])
        result = self.model.invoke([message])
        parsed = self.output_parser.parse(result.content)
        return parsed.dict()


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
