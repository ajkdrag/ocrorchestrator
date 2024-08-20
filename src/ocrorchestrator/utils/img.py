import base64
import imghdr
from base64 import b64decode
from io import BytesIO

from PIL import Image


def pil_to_base64(image):
    buffered = BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


def base64_to_pil(b64str):
    return Image.open(BytesIO(b64decode(b64str))).convert("RGB")


def get_image_mime_type(base64_image: str) -> str:
    """
    Determine the MIME type of a base64 encoded image.

    Args:
    base64_image (str): The base64 encoded image string.

    Returns:
    str: The MIME type of the image.
    """
    image_data = base64.b64decode(base64_image)
    image_file = BytesIO(image_data)
    image_type = imghdr.what(image_file)

    mime_type_map = {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "tiff": "image/tiff",
        "webp": "image/webp",
    }

    mime_type = mime_type_map.get(image_type, "application/octet-stream")

    return mime_type