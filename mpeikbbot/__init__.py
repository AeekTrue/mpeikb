import telebot
from telebot.types import Message, User
import time

from config import *
from logger import logger
from .utils import get_or_set_user_status, update_user_status, UserStatus

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN)


@bot.middleware_handler(update_types=['message'])
def inject_user_status(bot_instance, message: Message):
	message.from_user.status = get_or_set_user_status(message.from_user)


@bot.message_handler(commands=['help', 'start'])
def welcome(message: Message):
	chat_id = message.chat.id
	bot.send_message(chat_id, """Приветствуем тебя в Базе знаний МЭИ. Это проект студентов 1 курса.
	/publish - опубликовать конспект
	/search - искать конспекты""")


@bot.message_handler(commands=['search'])
def suggest_search(message: Message):
	chat_id = message.chat.id
	update_user_status(message.from_user, UserStatus.WAIT_SEARCH)
	bot.send_message(chat_id, """Перечисли все тэги которые тебе интересны.""")


@bot.message_handler(commands=['publish'])
def suggest_publish(message: Message):
	chat_id = message.chat.id
	update_user_status(message.from_user, UserStatus.WAIT_CONSPECTUS)
	bot.send_message(chat_id, """Пришли файл с конспектом или одну фотографию""")


@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def get_document(message: Message):
	chat_id = message.chat.id
	if message.from_user.status == UserStatus.WAIT_CONSPECTUS:
		bot.send_message(chat_id,
						 f"""Ты прислал мне {message.content_type}. Молодчина.
						Пришли мне тэги, для этого конспекта в формате <...>""")
		update_user_status(message.from_user, UserStatus.WAIT_TAG)
	else:
		bot.send_message("""И что мне с этим добром делать?""")


@bot.message_handler()
def get_message(message: Message):
	chat_id = message.chat.id
	if message.from_user.status == UserStatus.NEW:
		bot.send_message(chat_id, f"""Воспользуйтесь командой /help чтобы получить список доступных команд""")
	elif message.from_user.status == UserStatus.WAIT_SEARCH:
		bot.send_message(chat_id, f"""Сейчас поищим ага-ага..""")
		bot.send_message(chat_id, f"""Ничего не нашлось""")
		update_user_status(message.from_user, UserStatus.NEW)
	elif message.from_user.status == UserStatus.WAIT_CONSPECTUS:
		bot.send_message(chat_id, f"""Здесь нет конспекта, попробуйте еще раз.""")
	elif message.from_user.status == UserStatus.WAIT_TAG:
		bot.send_message(chat_id, f"""Отлично конспект принят!""")
		update_user_status(message.from_user, UserStatus.NEW)


if RESET_WEBHOOK:
	logger.warning('Removing webhook.')
	bot.remove_webhook()
	time.sleep(1)
	bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
	logger.success('Webhook is setup.')
else:
	logger.info('Webhook will not be changed')
