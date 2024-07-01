from enum import Enum

IMG_SIZE = (224, 224)


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
