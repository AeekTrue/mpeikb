import telebot
from telebot.types import Message, User
import time

from config import *
from logger import logger
from .types import UserStatus

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN)

main_keyboard = telebot.types.InlineKeyboardMarkup()
main_keyboard.add(telebot.types.InlineKeyboardButton('Искать конспект', callback_data='search'))
main_keyboard.add(telebot.types.InlineKeyboardButton('Отправить конспект', callback_data='publish'))


def send_conspectus(conspectus_id: int):
	pass


@bot.message_handler(commands=['start'])
def start_message(message: Message):
	bot.send_message(message.chat.id, 'Привет!', reply_markup=main_keyboard)


@bot.message_handler(commands=['help'])
def help_message(message: Message):
	pass


@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def get_document(message: Message):
	media_group_id = message.media_group_id
	if media_group_id is None:
		bot.send_message(message.chat.id, 'Single file')
	else:
		bot.send_message(message.chat.id, f'File from media group {media_group_id}')


if RESET_WEBHOOK:
	logger.warning('Removing webhook.')
	bot.remove_webhook()
	time.sleep(1)
	bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
	logger.success('Webhook is setup.')
else:
	logger.info('Webhook will not be changed')
