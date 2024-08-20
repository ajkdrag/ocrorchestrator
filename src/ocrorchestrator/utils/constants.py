from enum import Enum
from pathlib import Path

import torchvision.models as models
from langchain_google_vertexai import HarmBlockThreshold as HT
from vertexai.generative_models import HarmCategory as HC

IMG_SIZE = (224, 224)
PKG_ROOT = Path(__file__).parent.parent
PROJ_ROOT = PKG_ROOT.parent.parent
LOCAL_DIR = PROJ_ROOT.joinpath("data/local").as_posix()
LOCAL_REPO = PROJ_ROOT.joinpath("local/fs").as_posix()
GCP_ENV_VAR = "GOOGLE_APPLICATION_CREDENTIALS"

PRETRAINED_MODELS = {
    "resnet50": models.resnet50,
    "resnet18": models.resnet18,
}


class ErrorCode(Enum):
    SUCCESS = (200, "Success")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    NOT_FOUND = (404, "Not Found")
    PROCESSOR_NOT_FOUND = (405, "Processor Not Found")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    PROCESSING_ERROR = (502, "Processing Error")
    INITIALIZATION_ERROR = (503, "Initialization Error")
    PROCESS_CLEANUP_ERROR = (504, "Cleanup Error")
    API_CALL_ERROR = (511, "Api Call Error")
    REPO_GET_ERROR = (521, "Error reading file")
    REPO_OBJECT_DOWNLOAD_ERROR = (522, "Error downloading object")
    REPO_INITIALIZATION_ERROR = (523, "Error initializing repository")

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
