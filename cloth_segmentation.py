import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
import torch
import albumentations as albu

from iglovikov_helper_functions.utils.image_utils import load_rgb, pad, unpad
from iglovikov_helper_functions.dl.pytorch.utils import tensor_from_rgb_image
from cloths_segmentation.pre_trained_models import create_model

model = create_model("Unet_2020-10-30")
model.eval();

try:
    os.makedirs('in-images')
except:
    pass

def create_mask(image_path):
    image = load_rgb(image_path)

    transform = albu.Compose([albu.Normalize(p=1)], p=1)
    padded_image, pads = pad(image, factor=32, border=cv2.BORDER_CONSTANT)

    x = transform(image=padded_image)["image"]
    x = torch.unsqueeze(tensor_from_rgb_image(x), 0)

    with torch.no_grad():
      prediction = model(x)[0][0]

    mask = (prediction > 0).cpu().numpy().astype(np.uint8)
    mask = unpad(mask, pads)

    masked = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB) * 255

    # dilate the mask to make it more smooth
    kernel = np.ones((16,16),np.uint8)
    masked = cv2.dilate(masked, kernel, iterations = 1)

    # save the masked image with the same name with input image but with _masked suffix
    masked_file_name = image_path.split("/")[-1].split(".")[0] + "_masked.jpg"
    cv2.imwrite(f"./in-images/{masked_file_name}", masked)

    # return masked image file path
    return f"./in-images/{masked_file_name}"