# Telegram SDWebUI Bot
This project integrates a Telegram bot with a [Stable Diffusion server](https://github.com/AUTOMATIC1111/stable-diffusion-webui) for cloth segmentation. The bot allows users to interact with the cloth segmentation model through Telegram, providing an easier interface with the Stable Diffusion server.

Users must also install the local server of the Stable Diffusion server mentioned above before they can use this bot.

## Project Structure

```
.gitignore
bot.py
cloth_segmentation.py
README
requirements.txt
run.sh
sdwebui.py
```

### Files

- **[`bot.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22vscode-vfs%22%2C%22authority%22%3A%22github%22%2C%22path%22%3A%22%2Fphuchoang2603%2Ftelegram-sdwebui%2Fbot.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22b4579377-43f4-4678-a480-948e3652a349%22%5D "\phuchoang2603\telegram-sdwebui\bot.py")**: Contains the main logic for the Telegram bot.
- **[`cloth_segmentation.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22vscode-vfs%22%2C%22authority%22%3A%22github%22%2C%22path%22%3A%22%2Fphuchoang2603%2Ftelegram-sdwebui%2Fcloth_segmentation.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22b4579377-43f4-4678-a480-948e3652a349%22%5D "\phuchoang2603\telegram-sdwebui\cloth_segmentation.py")**: Contains code for cloth segmentation using image processing and machine learning techniques.
- **[`requirements.txt`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22vscode-vfs%22%2C%22authority%22%3A%22github%22%2C%22path%22%3A%22%2Fphuchoang2603%2Ftelegram-sdwebui%2Frequirements.txt%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22b4579377-43f4-4678-a480-948e3652a349%22%5D "\phuchoang2603\telegram-sdwebui\requirements.txt")**: Lists all the Python dependencies required for the project.
- **[`run.sh`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22vscode-vfs%22%2C%22authority%22%3A%22github%22%2C%22path%22%3A%22%2Fphuchoang2603%2Ftelegram-sdwebui%2Frun.sh%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22b4579377-43f4-4678-a480-948e3652a349%22%5D "\phuchoang2603\telegram-sdwebui\run.sh")**: Shell script to run the project.
- **[`sdwebui.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22vscode-vfs%22%2C%22authority%22%3A%22github%22%2C%22path%22%3A%22%2Fphuchoang2603%2Ftelegram-sdwebui%2Fsdwebui.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22b4579377-43f4-4678-a480-948e3652a349%22%5D "\phuchoang2603\telegram-sdwebui\sdwebui.py")**: Main program, also includes the prompt for the Stable Diffusion server.

## Setup

1. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

2. **Run the Project**:
    ```sh
    ./run.sh
    ```
