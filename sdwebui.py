import os
import requests
import base64
import time

sdurl = "http://192.168.1.4:7860"
IMAGE_SIZE = 384

try:
    os.makedirs('out-images')
except:
    pass

def img2img (positive_prompt, negative_prompt, image_path, masked_image_path):
    api_url = f"{sdurl}/sdapi/v1/img2img"
    # encode init image
    with open(image_path, 'rb') as file:
        image_data = file.read()
    encoded_in_image = base64.b64encode(image_data).decode('utf-8')
    # encode masked image
    with open(masked_image_path, 'rb') as file:
        masked_image_data = file.read()
    encoded_masked_image = base64.b64encode(masked_image_data).decode('utf-8')
    payload = {
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "init_images": [encoded_in_image],
        "mask": encoded_masked_image,
        "mask_blur": 64,
        "seed": -1,
        "sampler_name": "Euler a",
        "batch_size": 1,
        "steps": 20,
        "cfg_scale": 7,
        "width": IMAGE_SIZE,
        "height": IMAGE_SIZE,
        "restore_faces": True,
        "denoising_strength": 0.85,
        "resize_mode": 1,
        "alwayson_scripts": {
            "controlnet": {
            "args": [
                {
                "module": "openpose_full",
                "model": "control_v11p_sd15_openpose [cab727d4]",
                "resize_mode": 1,
                "processor_res": IMAGE_SIZE
                }
            ]
            }
        }
    }
    response = requests.post(api_url, json=payload)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    name = f"./out-images/{timestr}.jpg"

    if response.status_code == 200:
        response_data = response.json()
        encoded_result = response_data["images"][0]
        result_data = base64.b64decode(encoded_result)
        output_path = name
        with open(output_path, 'wb') as file:
            file.write(result_data)
        return name
    else:
        print("Error", response.text)
        return None

