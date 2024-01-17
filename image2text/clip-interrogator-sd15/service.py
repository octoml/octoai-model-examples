import torch
from io import BytesIO
from base64 import b64decode
from PIL import Image
from pydantic import BaseModel
from clip_interrogator import Config, Interrogator
from octoai.service import Service


class Prediction(BaseModel):
    image: str
    mode: str = "default"


class Completion(BaseModel):
    description: str


class ImageService(Service):

    def setup(self):
        # Use the same clip model as in SDXL
        self.clip_interrogator = Interrogator(
            Config(
                clip_model_name="ViT-L-14/openai",
                clip_model_path='cache',
                download_cache=True,
                device="cuda:0" if torch.cuda.is_available() else "cpu"
            )
        )

    def infer(self, input: Prediction) -> Completion:
        description = None
        image = Image.open(BytesIO(b64decode(input.image)))
        if input.mode == "fast":
            description = self.clip_interrogator.interrogate_fast(image)
        elif input.mode == "classic":
            description = self.clip_interrogator.interrogate_classic(image)
        elif input.mode == "negative":
            description = self.clip_interrogator.interrogate_negative(image)
        else:
            description = self.clip_interrogator.interrogate(image)

        return Completion(
            description=description
        )
