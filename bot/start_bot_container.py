from aiogram import Bot
from bot_data import config


bot = Bot(token=config.BOT_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
