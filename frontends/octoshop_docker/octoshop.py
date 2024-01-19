# A streamlit frontend for running OctoShop multimodal model cocktail!
import streamlit as st
from octoai.client import Client
from octoai.clients.image_gen import ImageGenerator


from io import BytesIO
from base64 import b64encode, b64decode
from PIL import Image, ExifTags
import os
import time

CLIP_ENDPOINT_URL = os.environ["CLIP_ENDPOINT_URL"]
OCTOAI_API_TOKEN = os.environ["OCTOAI_API_TOKEN"]

client = Client(OCTOAI_API_TOKEN)
image_gen = ImageGenerator(token=OCTOAI_API_TOKEN)

# Encodes an PIL image into a string
def image_to_base64(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_b64 = b64encode(buffered.getvalue()).decode("utf-8")
    return img_b64

# Rotates image based on exif data
# (useful if you're taking a snapshot from your phone)
def rotate_image(image: Image) -> Image:
    try:
        # Rotate based on Exif Data
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif = image._getexif()
        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)
        return image
    except:
        return image

# Rescales the image to an appropriate resolution
def rescale_image(image: Image) -> Image:
    w, h = image.size
    if w == h:
        return image.resize((1024, 1024))
    else:
        if w > h:
            new_height = h
            new_width = int(h * 1216 / 832 )
        else:
            new_width = w
            new_height = int(w * 1216 / 832)
        left = (w - new_width)/2
        top = (h - new_height)/2
        right = (w + new_width)/2
        bottom = (h + new_height)/2
        image = image.crop((left, top, right, bottom))
        if w > h:
            return image.resize((1216, 832))
        else:
            return image.resize((832, 1216))

# Takes in an image, transformation string, and style
# string and returns a transformed image
def octoshop(image: Image, transformation: str, style: str) -> Image:
    # Step 1: CLIP captioning
    output = client.infer(
        endpoint_url=CLIP_ENDPOINT_URL+'/predict',
        inputs={
            "image": image_to_base64(image),
            "mode": "fast"
        }
    )
    clip_labels = output["completion"]["labels"]
    top_label = clip_labels.split(',')[0]

    # Step 2: LLM transformation
    llm_prompt = '''
    Human: {}: {}
    AI: '''.format(transformation, top_label)
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Keep your responses short and limited to one sentence."
            },
            {
                "role": "user",
                "content": llm_prompt
            }
        ],
        model="mistral-7b-instruct-fp16",
        max_tokens=128,
        presence_penalty=0,
        temperature=0.1,
        top_p=0.9,
    )
    llm_image_desc = completion.choices[0].message.content

    # Step 3: SDXL+controlnet transformation
    w, h = image.size
    image_gen_response = image_gen.generate(
        engine="controlnet-sdxl",
        controlnet="depth_sdxl",
        controlnet_conditioning_scale=0.4,
        controlnet_image=image_to_base64(image),
        prompt=llm_image_desc,
        negative_prompt="blurry photo, distortion, low-res, poor quality",
        width=w,
        height=h,
        num_images=1,
        sampler="DPM_PLUS_PLUS_2M_KARRAS",
        steps=20,
        cfg_scale=7.5,
        use_refiner=True,
        # We comment this out to get a different result
        # every time!
        # seed=1,
        style_preset=style
    )
    images = image_gen_response.images

    # Display generated image from OctoAI
    pil_image = images[0].to_pil()
    return top_label, llm_image_desc, pil_image



st.set_page_config(layout="wide", page_title="OctoShop: Space Travel Edition")

st.write("## OctoShop: Space Travel Edition")

# You can edit those settings to customize your
# own OctoShop model cocktail
transformation = "set the image description into space"
style = "3d-model"

my_upload = st.file_uploader("Take a snap or upload a photo", type=["png", "jpg", "jpeg"])

if my_upload is not None:
    if st.button('OctoShop!'):
        # Preprocess
        input_img = Image.open(my_upload)
        input_img = rotate_image(input_img)
        input_img = rescale_image(input_img)
        # Go through the OctoShop pipeline
        label, image_desc, output_img = octoshop(input_img, transformation, style)
        # Display the results
        col0, col1 = st.columns(2)
        col0.image(input_img)
        col1.image(output_img)
