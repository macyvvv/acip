from __future__ import annotations
import base64
from dataclasses import dataclass
from openai import OpenAI

@dataclass(frozen=True, slots=True)
class ImageResult:
    image_bytes: bytes
    revised_prompt: str | None

class OpenAIImageAdapter:
    def __init__(self, api_key: str | None = None):
        self.client = OpenAI(api_key=api_key)

    def generate(self, *, prompt: str, model: str, size: str, quality: str, output_format: str) -> ImageResult:
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            output_format=output_format,
            n=1,
        )
        item = response.data[0]
        if not item.b64_json:
            raise RuntimeError("Images API returned no base64 image data")
        return ImageResult(
            image_bytes=base64.b64decode(item.b64_json),
            revised_prompt=getattr(item, "revised_prompt", None),
        )
