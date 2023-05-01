import requests
from PIL import Image
from io import BytesIO
import numpy as np
import tensorflow as tf
from keras import backend as K
from huggingface_hub import from_pretrained_keras
import openai
from dotenv import load_dotenv
import os

# Load both models at the beginning
K.set_image_data_format('channels_last')
models = {}

# Load models for detecting real vs AI human faces
model = from_pretrained_keras("poojakabber1997/ResNetDallE2Fakes")
model.compile(optimizer='adam', loss='binary_crossentropy')
models["poojakabber1997/ResNetDallE2Fakes"] = model

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to generate AI image
def generate_image(input_image):
    # Convert the input image to JPEG format
    input_image = input_image.convert("RGB")
    input_image_file = BytesIO()
    input_image.save(input_image_file, format="PNG")

    # Generate the AI image
    response = openai.Image.create_variation(
        image=input_image_file.getvalue(),
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']

    # Download the image from the URL
    image_data = requests.get(image_url).content

    return Image.open(BytesIO(image_data))




# Function to detect if an image is of a real human face or an AI generated face
def get_prediction(image):
    model_key = "poojakabber1997/ResNetDallE2Fakes"
    input_shape = (1, 3, 180, 180)
    model = models[model_key]
    channels_first = False
    image = Image.fromarray(image.astype('uint8'), 'RGB').resize(input_shape[2:])
    image = np.array(image).astype(np.float32)
    image = image / 255

    if channels_first:
        image = np.transpose(image, (2, 0, 1))

    image = np.expand_dims(image, axis=0)

    if channels_first:
        image = np.transpose(image, (0, 2, 3, 1))

    prediction = model.predict(image)
    real_prob = prediction[0][0]
    fake_prob = 1 - real_prob

    if real_prob > fake_prob:
        return "Real Human Face", real_prob
    else:
        return "AI Generated Face", fake_prob


