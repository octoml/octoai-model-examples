"""
test_request.py.

This program makes an example request to your endpoint.
You typically use this program to verify that your service
works correctly:

- After `octoai run` (local development).
  No extra arguments are needed in this case.

  Example:
  `octoai run --command "python test_request.py"`

- After `octoai deploy` (remote deployment).
  Provide your endpoint's host name and port as arguments.

  Example:
  `python test_request.py --endpoint https://myapp123.octoai.cloud`

This program also serves as basic example on how to use the
Python client of the OctoAI SDK. As you develop your service,
you may have to change the inputs in this program to match
what your service expects.
"""
import argparse
import io
import requests
from base64 import b64encode, b64decode
from io import BytesIO
from octoai.client import Client
from PIL import Image


def image_to_base64(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_b64 = b64encode(buffered.getvalue()).decode("utf-8")
    return img_b64

def save_image(image_base64, filename):
    image = Image.open(io.BytesIO(b64decode(image_base64)))
    image.save(f"{filename}.png")


def main(endpoint):
    r = requests.get('https://raw.githubusercontent.com/tmoreau89/image-assets/main/octoshop/moby.jpeg')
    image = Image.open(BytesIO(r.content))
    inputs = {
        "input": {
            "image": image_to_base64(image),
            "mode": "fast"
        }
    }

    # create an OctoAI client
    client = Client()

    # perform inference
    response = client.infer(endpoint_url=f"{endpoint}/infer", inputs=inputs, )

    # Get the results out
    description = response["output"]["description"]
    print("CLIP interrogator description from SD1.5: {}".format(description))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", type=str, default="http://localhost:8080")

    args = parser.parse_args()
    main(args.endpoint)
