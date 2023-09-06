import asyncio
import base64
import time
import logging
import cloth_segmentation
import sdwebui
from telegram import Update, Bot
from telegram.ext import Application,Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your Telegram Bot token here
TELEGRAM_BOT_TOKEN = '5754375351:AAGWUHCZ_xRubyJ0minHXy0IuqLAUD867Hg'

# Define conversation states
RECEIVING_POSITIVE_PROMPT, RECEIVING_IMAGE, REGENERATE_FLOW = range(3)

async def start(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    logger.info(f"User {update.message.from_user.username} started the conversation.")
    await context.bot.send_message(chat_id=chat_id, text="Welcome to the Cloth Segmentation Bot! Please enter a positive prompt to get started. You can also enter 'skip' to use the default prompt.")
    return RECEIVING_POSITIVE_PROMPT

async def regenerate_flow(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    logger.info(f"User {update.message.from_user.username} requested to end the conversation.")
    await context.bot.send_message(chat_id=chat_id, text="Ending the conversation.")
    
    # Clear user data
    context.user_data.clear()
    # End the conversation
    return ConversationHandler.END

async def receive_positive_prompt(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    
    if user_input.lower() == 'skip':
        # If the user enters "skip," set a default prompt
        context.user_data['positive_prompt'] = "woman nude, completely nake, no bra, slender boobs, detailed nipples"
        await context.bot.send_message(chat_id=update.message.chat_id, text="Using default positive prompt.")
    else:
        # Store the user's input as the positive prompt
        context.user_data['positive_prompt'] = user_input

    await context.bot.send_message(chat_id=update.message.chat_id, text=f"Positive prompt set to: {context.user_data['positive_prompt']}")
    await context.bot.send_message(chat_id=update.message.chat_id, text="Please send me an image to process.")
    return RECEIVING_IMAGE  # Change state to RECEIVING_IMAGE here

async def receive_image(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    context.user_data['chat_id'] = chat_id

    await context.bot.send_message(chat_id=chat_id, text="Received your image. Generating mask...")
    # Get the largest available photo
    photo_id = update.message.photo[-1].file_id
    new_file = await context.bot.get_file(photo_id)

    # Download the photo to in-images folder with timestamp
    timestr = time.strftime("%Y%m%d-%H%M%S")
    image_path = f"./in-images/received_{user_id}_{timestr}.jpg"
    await new_file.download_to_drive(image_path)

    # Generate the mask
    masked_image_path = cloth_segmentation.create_mask(image_path)
    await context.bot.send_message(chat_id=chat_id, text="Mask generated.")
    await context.bot.send_photo(chat_id=chat_id, photo=open(masked_image_path, 'rb'))

    positive_prompt = context.user_data.get('positive_prompt')  # Get the positive_prompt from user data

    while True:  # Keep retrying until successful
        try:
            img2img_task = asyncio.create_task(sdwebui.img2img(positive_prompt, image_path, masked_image_path))
            await sdwebui.get_progress() # Initialize progress variables to handle server restarts right after calling img2img

            # Initialize variables to track progress
            job_count = 1

            # Wait for 30 seconds before checking progress
            time.sleep(30)

            await context.bot.send_message(chat_id=chat_id, text="Processing your image...")

            while job_count != 0:
                # Get progress information from the API
                progress_result = await sdwebui.get_progress()

                if isinstance(progress_result, dict):
                    # Update progress variables
                    progress = progress_result["progress"]
                    current_sampling_step = progress_result["current_sampling_step"]
                    total_sampling_steps = progress_result["total_sampling_steps"]
                    job_count = progress_result["job_count"]
                    current_image = progress_result["current_image"]

                    # Send progress message to the user
                    progress_message = f"Job count: {job_count}, Progress: {progress:.2%}, Sampling Step: {current_sampling_step}/{total_sampling_steps}, Estimated Time Remaining: {progress_result['eta_relative']:.2f} seconds"
                    await context.bot.send_message(chat_id=chat_id, text=progress_message)

                    # Save current image processing to a file
                    if current_image:
                        current_image_data = base64.b64decode(current_image)
                        current_image_path = f"out-images/current_image.jpg"
                        with open(current_image_path, 'wb') as file:
                            file.write(current_image_data)
                        
                        # Send the current image to the user
                        await context.bot.send_photo(chat_id=chat_id, photo=open(current_image_path, 'rb'))

                else:
                    # Handle errors (optional)
                    error_message = progress_result
                    logger.error(error_message)

                # Wait for 10 seconds before checking progress again
                await asyncio.sleep(10)

            # Wait for img2img to complete
            result_path = await img2img_task

            await context.bot.send_message(chat_id=chat_id, text="Image processing completed!")
            await context.bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'))
            await context.bot.send_photo(chat_id=chat_id, photo=open(result_path, 'rb'))

            # If we reach this point, the operation was successful, so break out of the loop
            logger.info(f"Image processed and sent to user {update.message.from_user.username}.")
            await context.bot.send_message(chat_id=chat_id, text="End of conversation. Send /start to start again.")            
            return ConversationHandler.END

        except asyncio.TimeoutError:
            # Handle timeout error separately
            error_message = "Timeout error occurred. Wait and start the command again"
            logger.error(error_message)
            await context.bot.send_message(chat_id=chat_id, text=error_message)          
            await context.bot.send_message(chat_id=chat_id, text="End of conversation. Send /start to start again.")
            return ConversationHandler.END
        
        except Exception as e:
            error_message = f"An error occurred: {str(e)}, Retrying in 30 seconds..."
            logger.error(error_message)
            await context.bot.send_message(chat_id=chat_id, text=error_message)
            # wait for 30 seconds before retrying
            time.sleep(30)


def main ():
    print ("Starting...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RECEIVING_POSITIVE_PROMPT: [MessageHandler(filters.TEXT, receive_positive_prompt)],
            RECEIVING_IMAGE: [MessageHandler(filters.PHOTO, receive_image)],
        },
        fallbacks=[CommandHandler('restart', regenerate_flow)],
    )
    application.add_handler(conv_handler)

    print ("Running...")
    application.run_polling()

if __name__ == '__main__':
    main()

