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
	bot.send_message(chat_id, """Привет! Перед тобой коллекция знаний НИУ МЭИ. Это проект студентов 1 курса.
	/publish - загрузить конспект в Базу
	/search - получить конспекты""")


@bot.message_handler(commands=['search'])
def suggest_search(message: Message):
	chat_id = message.chat.id
	update_user_status(message.from_user, UserStatus.WAIT_SEARCH)
	bot.send_message(chat_id, """Напиши все теги нужных конспектов.""")


@bot.message_handler(commands=['publish'])
def suggest_publish(message: Message):
	chat_id = message.chat.id
	update_user_status(message.from_user, UserStatus.WAIT_CONSPECTUS)
	bot.send_message(chat_id, """Отправь файл с конспектом или фотографию""")


@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def get_document(message: Message):
	chat_id = message.chat.id
	if message.from_user.status == UserStatus.WAIT_CONSPECTUS:
		bot.send_message(chat_id,
						 f"""Ты прислал мне {message.content_type}! Едем дальше!
						Жду от тебя теги, для этого конспекта, например:
						`матан 1курс лекции 1семестр pdf история etc.` """)
		update_user_status(message.from_user, UserStatus.WAIT_TAG)
	else:
		bot.send_message("""Правильно понимаю, что ты хочешь опубликовать этот конспект?
		Тогда пришли тэги к нему)""")
		update_user_status(message.from_user, UserStatus.WAIT_TAG)


@bot.message_handler()
def get_message(message: Message):
	chat_id = message.chat.id
	if message.from_user.status == UserStatus.NEW:
		bot.send_message(chat_id, f"""Воспользуйтесь командой /help чтобы получить список доступных команд""")
	elif message.from_user.status == UserStatus.WAIT_SEARCH:
		bot.send_message(chat_id, f"""Уже нашел, отправляю""")
		#метод выдачи запроса
		bot.send_message(chat_id, f"""Ничего не нашлось""")
		update_user_status(message.from_user, UserStatus.NEW)
	elif message.from_user.status == UserStatus.WAIT_CONSPECTUS:
		bot.send_message(chat_id, f"""Вы прислали не конспект""")
	elif message.from_user.status == UserStatus.WAIT_TAG:
		bot.send_message(chat_id, f"""Выдал базу, принимаю!""")
		update_user_status(message.from_user, UserStatus.NEW)


if RESET_WEBHOOK:
	logger.warning('Removing webhook.')
	bot.remove_webhook()
	time.sleep(1)
	bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
	logger.success('Webhook is setup.')
else:
	logger.info('Webhook will not be changed')
