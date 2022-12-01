import telebot
from telebot.types import Message, User
import time

from config import TOKEN, ADMIN_ID, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH
from logger import logger
from .utils import get_or_set_user_status, update_user_status, UserStatus

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN)


@bot.middleware_handler(update_types=['message'])
def inject_user_status(bot_instance, message: Message):
	message.from_user.status = get_or_set_user_status(message.from_user)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, """Приветствуем тебя в Базе знаний МЭИ. Это проект студентов 1 курса.""")


logger.warning('Removing webhook.')
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
logger.success('Webhook is setup.')
