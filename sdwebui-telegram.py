import os
import asyncio
import aiohttp
import base64
import time
import logging
from cloth_segmentation import cloth_segmentation
from telegram import Update, Bot
from telegram.ext import Application,Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

try:
    os.makedirs('out-images')
except:
    pass

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your Telegram Bot token here
TELEGRAM_BOT_TOKEN = '5754375351:AAGWUHCZ_xRubyJ0minHXy0IuqLAUD867Hg'

sdurl = "http://127.0.0.1:7860"
IMAGE_SIZE = 384

# Define conversation states
CHOOSING, RECEIVING_IMAGE = range(2)

def encode_image(image_path):
    with open(image_path, 'rb') as file:
        image_data = file.read()
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    return encoded_image

async def get_progress(context: CallbackContext):
    while True:
        progress_url = f"{sdurl}/sdapi/v1/progress"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(progress_url) as response:
                if response.status == 200:
                    progress_info = await response.json()
                    progress = progress_info.get("progress", 0.0)
                    current_sampling_step = progress_info.get("state", {}).get("sampling_step", 0)
                    total_sampling_steps = progress_info.get("state", {}).get("sampling_steps", 1)
                    progress_text = f"Progress: {progress:.2%}, Sampling Step: {current_sampling_step}/{total_sampling_steps}"
                    await context.bot.send_message(chat_id=context.user_data['chat_id'], text=progress_text)
                    
                    if total_sampling_steps - current_sampling_step == 1:
                        break  # Stop calling the progress API when this condition is met
                else:
                    error_message = "Error fetching progress: " + await response.text()
                    await context.bot.send_message(chat_id=context.user_data['chat_id'], text=error_message)

        await asyncio.sleep(10)  # Wait for 5 seconds before checking progress again

async def img2img(positive_prompt, negative_prompt, image_path, masked_image_path):
    api_url = f"{sdurl}/sdapi/v1/img2img"
    payload = {
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "init_images": [encode_image(image_path)],
        "mask": encode_image(masked_image_path),
        "mask_blur_x": 0,
        "mask_blur_y": 0,
        "sampler_name": "Euler a",
        "restore_faces": True,
        "steps": 20,
        "cfg_scale": 8,
        "width": IMAGE_SIZE,
        "height": IMAGE_SIZE,
        "denoising_strength": 0.85,
        "resize_mode": 1,
        "inpainting_fill": 1,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 200,
        # "alwayson_scripts": {
        #     "controlnet": {
        #     "args": [
        #         {
        #         "module": "openpose_full",
        #         "model": "control_v11p_sd15_openpose [cab727d4]",
        #         "resize_mode": 1,
        #         "processor_res": IMAGE_SIZE
        #         }
        #     ]
        #     }
        # }
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
                error_message = "Error: " + await response.text()
                print(error_message)
                return None

async def start(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    logger.info(f"User {update.message.from_user.username} started the conversation.")
    await context.bot.send_message(chat_id=chat_id, text="Send me an image to process.")
    return RECEIVING_IMAGE

async def receive_image(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    context.user_data['chat_id'] = chat_id

    if update.message.photo:
        # Get the largest available photo
        photo_id = update.message.photo[-1].file_id
        new_file = await context.bot.get_file(photo_id)
        # Download the photo to in-images folder with timestamp
        timestr = time.strftime("%Y%m%d-%H%M%S")
        image_path = f"./in-images/received_{user_id}_{timestr}.jpg"
        await new_file.download_to_drive(image_path)
        masked_image_path = cloth_segmentation(image_path)
        positive_prompt = "woman nude, nake, breasts, slender boobs, detailed nipples"
        negative_prompt = "ugly, deformed, deformityc, disfigured, malformed, ugliness, blurry, disfigured, mutation, mutated, extra limbs, bad anatomy, long body, cropped head, cropped face, two women, anatomical nonsense, malformed hands, long neck, missing limb, floating limbs, disconnected limbs"

        # Start the get_progress task in the background
        asyncio.create_task(get_progress(context))

        # Run img2img task
        result_path = await img2img(positive_prompt, negative_prompt, image_path, masked_image_path)

        # Send the processed image back to the user
        await context.bot.send_photo(chat_id=chat_id, photo=open(result_path, 'rb'))
        await context.bot.send_message(chat_id=chat_id, text="Processing completed!")

        logger.info(f"Image processed and sent to user {update.message.from_user.username}.")
        return ConversationHandler.END
    
    else:
        await context.bot.send_message(chat_id=chat_id, text="Please send an image.")
        logger.warning(f"User {update.message.from_user.username} did not send an image as expected.")
        return RECEIVING_IMAGE


def main ():
    print ("Starting...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RECEIVING_IMAGE: [MessageHandler(filters.PHOTO, receive_image)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)

    print ("Running...")
    application.run_polling()

if __name__ == '__main__':
    main()

