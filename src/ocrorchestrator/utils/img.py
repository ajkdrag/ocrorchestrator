from base64 import b64decode
from io import BytesIO

from PIL import Image


def base64_to_pil(b64str):
    return Image.open(BytesIO(b64decode(b64str))).convert("RGB")
