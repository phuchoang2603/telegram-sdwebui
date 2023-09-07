import os
import asyncio
import aiohttp
import base64
import time
from cloth_segmentation import create_mask
import requests

sdurl = "http://127.0.0.1:7860"
# sdurl = "http://192.168.1.4:7860"
IMAGE_SIZE = 384

try:
    os.makedirs('out-images')
except:
    pass

def encode_image(image_path):
    with open(image_path, 'rb') as file:
        image_data = file.read()
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    return encoded_image

async def get_progress():
    progress_url = f"{sdurl}/sdapi/v1/progress"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(progress_url) as response:
            if response.status == 200:
                progress_info = await response.json()
                
                progress = progress_info.get("progress", 0.0)
                eta_relative = progress_info.get("eta_relative", 0.0)
                current_sampling_step = progress_info.get("state", {}).get("sampling_step", 0)
                total_sampling_steps = progress_info.get("state", {}).get("sampling_steps", 1)
                job_count = progress_info.get("state", {}).get("job_count", 0)
                current_image = progress_info.get("current_image", "")
                progress_result = {
                    "progress": progress,
                    "eta_relative": eta_relative,
                    "current_sampling_step": current_sampling_step, 
                    "total_sampling_steps": total_sampling_steps,
                    "job_count": job_count,
                    "current_image": current_image
                }
                
                return progress_result
            
            else:
                return ("Error fetching progress:", await response.text())

async def img2img(positive_prompt, image_path, masked_image_path):
    api_url = f"{sdurl}/sdapi/v1/img2img"
    payload = {
        "prompt": positive_prompt,
        "negative_prompt": "ugly, deformed, deformityc, disfigured, malformed, ugliness, blurry, disfigured, mutation, mutated, extra limbs, bad anatomy, long body, cropped head, cropped face, two women, anatomical nonsense, malformed hands, long neck, missing limb, floating limbs, disconnected limbs",
        "init_images": [encode_image(image_path)],
        "mask": encode_image(masked_image_path),
        "sampler_name": "Euler a",
        "restore_faces": True,
        "steps": 20,
        "cfg_scale": 10,
        "width": IMAGE_SIZE,
        "height": IMAGE_SIZE,
        "denoising_strength": 0.7,
        "resize_mode": 1,
        "inpainting_fill": 1,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 100,
        "alwayson_scripts": {
            "controlnet": {
            "args": [
                {
                "module": "openpose_full",
                "model": "control_v11p_sd15_openpose [cab727d4]",
                "resize_mode": 1,
                "processor_res": IMAGE_SIZE,
                "lowvram": True,
                "pixel_perfect": True,
                }
            ]
            }
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload) as response:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            name = f"./out-images/{timestr}.jpg"

            if response.status == 200:
                response_data = await response.json()
                encoded_result = response_data["images"][0]
                result_data = base64.b64decode(encoded_result)
                output_path = name
                with open(output_path, 'wb') as file:
                    file.write(result_data)
                return name
            else:
                return ("Error", await response.text())

# Debugging
# async def main():
#     image_path = "in-images/366021029_259451880196838_9190101119937173386_n.jpg"
#     masked_image_path = create_mask(image_path)
#     positive_prompt = "woman nude, completely nake, breasts, slender boobs, detailed nipples"

#     while True:  # Keep retrying until successful
#         try:
#             img2img_task = asyncio.create_task(img2img(positive_prompt, image_path, masked_image_path))

#             # Initialize variables to track progress
#             job_count = 1

#             # Wait for 5 seconds before checking progress
#             await asyncio.sleep(5)

#             print ("tracking progress") # Debugging

#             while job_count != 0:
#                 # Get progress information from the API
#                 progress_result = await get_progress()

#                 if isinstance(progress_result, dict):
#                     # Update progress variables
#                     progress = progress_result["progress"]
#                     current_sampling_step = progress_result["current_sampling_step"]
#                     total_sampling_steps = progress_result["total_sampling_steps"]
#                     job_count = progress_result["job_count"]
#                     current_image = progress_result["current_image"]

#                     # Send progress message to the user
#                     progress_message = f"Job count: {job_count}, Progress: {progress:.2%}, Sampling Step: {current_sampling_step}/{total_sampling_steps}, Estimated Time Remaining: {progress_result['eta_relative']:.2f} seconds"

#                     # Save current image processing to a file
#                     if current_image:
#                         current_image_data = base64.b64decode(current_image)
#                         output_path = f"out-images/current_image.jpg"
#                         with open(output_path, 'wb') as file:
#                             file.write(current_image_data)

#                     print (progress_message)

#                 else:
#                     # Handle errors (optional)
#                     error_message = progress_result
#                     print (error_message)

#                 # Wait for 5 seconds before checking progress again
#                 await asyncio.sleep(5)

#             # Wait for img2img to complete
#             result_path = await img2img_task

#             print (result_path)

#             # If we reach this point, the operation was successful, so break out of the loop
#             break
    
#         except Exception as e:
#             error_message = f"An error occurred: {str(e)}, Retrying..."
#             # wait for 10 seconds before retrying
#             await asyncio.sleep(10)
#             print (error_message)


# if __name__ == "__main__":
#     asyncio.run(main())