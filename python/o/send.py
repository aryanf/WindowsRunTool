from message import (MainCommandMessage, SubCommandMessage, get_download_dir)
import telegram as telegram_bot
import asyncio
import pyperclip
from PIL import ImageGrab
import os

# fill in your telegram token and chat id
TELEGRAM_TOKEN = 'telegram_token'
TELEGRAM_CHAT_ID = 'telegram_chat_id'


def main(message: MainCommandMessage):
    '''
Send message to default service (Telegram)
'''
    new_message = SubCommandMessage(message.env, message.num, message.switch_1, message.switch_2)
    # lets say default service is Telegram
    telegram(new_message)


def telegram(message: SubCommandMessage):
    '''
Send switch1 to Telegram, if switch1 is not set, send clipboard content
'''
    content = message.switch_1
    is_image = False
    image_path = None
    if not content:
        image = ImageGrab.grabclipboard()
        if image:
            image_path = os.path.join(get_download_dir(), "clipboard_image.png")
            image.save(image_path)
            is_image = True
        else:
            content = pyperclip.paste()
    try:
        if is_image:
            asyncio.run(_send_image_to_telegram(image_path))
        else:
            asyncio.run(_send_text_to_telegram(content))
    except Exception as e:
        input(f'Error: {e}')
        exit()


async def _send_text_to_telegram(content):
    bot = telegram_bot.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=content)


async def _send_image_to_telegram(image_path):
    bot = telegram_bot.Bot(token=TELEGRAM_TOKEN)
    with open(image_path, 'rb') as image_file:
        await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image_file)

