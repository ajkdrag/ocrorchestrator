from enum import Enum

import torchvision.models as models
from langchain_google_vertexai import HarmBlockThreshold as HT
from vertexai.generative_models import HarmCategory as HC

IMG_SIZE = (224, 224)

PRETRAINED_MODELS = {
    "resnet50": models.resnet50,
    "resnet18": models.resnet18,
}


class ErrorCode(Enum):
    SUCCESS = (200, "Success")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    NOT_FOUND = (404, "Not Found")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    PROCESSOR_NOT_FOUND = (501, "Processor Not Found")
    PROCESSING_ERROR = (502, "Processing Error")
    INITIALIZATION_ERROR = (503, "Initialization Error")

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


SAFETY_SETTINGS = {
    HC.HARM_CATEGORY_UNSPECIFIED: HT.BLOCK_NONE,
    HC.HARM_CATEGORY_DANGEROUS_CONTENT: HT.BLOCK_NONE,
    HC.HARM_CATEGORY_HATE_SPEECH: HT.BLOCK_NONE,
    HC.HARM_CATEGORY_HARASSMENT: HT.BLOCK_NONE,
    HC.HARM_CATEGORY_SEXUALLY_EXPLICIT: HT.BLOCK_NONE,
}
