import telebot
from telebot.types import Message, User
import time

from config import *
from logger import logger
from .types import UserStatus
from .db import get_or_set_user_status, update_user_status, register_new_file_id, get_current_file_for_user, \
	create_conspectus, find_conspectuses
from .utils import parse_tags

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN)


def send_conspectus(chat_id, conspectus):
	logger.debug(f'sending {conspectus.file_id}')
	caption = f'{" ".join(conspectus.conspectus_tags)}\nРейтинг конспекта: {conspectus.rating}'
	if conspectus.file_type == 'photo':
		bot.send_photo(chat_id, conspectus.file_id,
					   caption=caption)
	elif conspectus.file_type == 'document':
		bot.send_document(chat_id, conspectus.file_id,
						  caption=caption,
						  allow_sending_without_reply=True)
	elif conspectus.file_type == 'video':
		bot.send_video(chat_id, conspectus.file_id, caption=caption)
	elif conspectus.file_type == 'audio':
		bot.send_audio(chat_id, conspectus.file_id, caption=caption)
	else:
		logger.error(f'Unknown file type {conspectus.file_type = }')
		bot.send_message(chat_id, 'Не удалось отправить файл обратитесь к разработчику')

@bot.middleware_handler(update_types=['message'])
def inject_user_status(bot_instance, message: Message):
	message.from_user.status = get_or_set_user_status(message.from_user)


@bot.message_handler(commands=['help', 'start'])
def welcome(message: Message):
	chat_id = message.chat.id
	bot.send_message(chat_id, """Привет! Перед Вами коллекция знаний НИУ МЭИ. Это проект студентов 1 курса.
	/publish - загрузить конспект в Базу
	/search - получить конспекты""")


@bot.message_handler(commands=['search'])
def suggest_search(message: Message):
	chat_id = message.chat.id
	update_user_status(message.from_user, UserStatus.WAIT_SEARCH)
	bot.send_message(chat_id, """Напишите все теги нужных Вам конспектов.""")


@bot.message_handler(commands=['publish'])
def suggest_publish(message: Message):
	chat_id = message.chat.id
	update_user_status(message.from_user, UserStatus.WAIT_CONSPECTUS)
	bot.send_message(chat_id, """Отправьте файл с конспектом или фотографию""")


def get_file_id_from_message(message: Message):
	logger.debug('determine file_id')
	if message.content_type == 'document':
		return message.document.file_id
	elif message.content_type == 'photo':
		return message.photo[0].file_id
	elif message.content_type == 'video':
		return message.video.file_id
	elif message.content_type == 'audio':
		return message.audio.file_id


content_type_translation = {
	'photo': 'фото',
	'document': 'файл',
	'video': 'видео',
	'audio': 'аудио',
}


@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def get_document(message: Message):
	"""При получении медиафайла бот отмечает этот файл,
	как редактируемый пользоватетем в данный момент,
	и переходит в режим ожидания тегов для этого файла."""
	chat_id = message.chat.id
	if message.from_user.status == UserStatus.WAIT_CONSPECTUS:
		bot.send_message(chat_id,
						 f"""Вы прислали {content_type_translation[message.content_type]}!
						 Едем дальше! Отправьте мне теги, для этого конспекта, например:
						`матан 1курс лекции 1семестр pdf история etc.` """)
	if message.from_user.status == UserStatus.WAIT_TAG:
		bot.send_message(chat_id, """Похоже вы хотите отправить сразу несколько файлов, к сожалению так нельзя.
		Объедините файлы в один и создайте конспект заново. /publish""")
		update_user_status(message.from_user, UserStatus.NEW)
	else:
		bot.send_message(chat_id,
						 """Правильно понимаю, что Вы хотите опубликовать этот конспект?
						Тогда пришлите теги к нему, например:
						`матан 1курс лекции 1семестр pdf история etc.`""")
	file_id = get_file_id_from_message(message)
	register_new_file_id(message.from_user.id, file_id, message.content_type)
	update_user_status(message.from_user, UserStatus.WAIT_TAG)


@bot.message_handler()
def get_message(message: Message):
	chat_id = message.chat.id
	if message.from_user.status == UserStatus.NEW:
		bot.send_message(chat_id, f"""Воспользуйтесь командой /help чтобы получить список доступных команд""")
	elif message.from_user.status == UserStatus.WAIT_SEARCH:
		tags = parse_tags(message.text)
		bot.send_message(chat_id, f"""Ищу конспекты с такими тегами: {' '.join(tags)}""")
		conspectuses = find_conspectuses(tags)
		if len(conspectuses) > 0:
			bot.send_message(message.chat.id, "Вот что мне удалось найти по вашему запросу")
			count = 0
			for conspectus in conspectuses:
				send_conspectus(message.chat.id, conspectus)
				count += 1
				if count >= 10:
					bot.send_message(message.chat.id, "Отправлены первые 10 конспектов")
					break
		else:
			bot.send_message(chat_id, f"""Ничего не нашлось""")
		update_user_status(message.from_user, UserStatus.NEW)
	elif message.from_user.status == UserStatus.WAIT_CONSPECTUS:
		bot.send_message(chat_id, f"""Вы прислали не конспект. Отправьте, например, файл или фото""")
	elif message.from_user.status == UserStatus.WAIT_TAG:
		file = get_current_file_for_user(message.from_user.id)
		if file.file_id == '':
			logger.error(f'Current file for user {message.from_user.id} not found.')
			bot.send_message(chat_id, """Что-то пошло не так. Попробуйте создать конспект заново командой /publish""")
		else:
			tags = parse_tags(message.text)
			create_conspectus(file.file_id, file.file_type, tags)
			bot.send_message(chat_id, f"""Ваш конспект принят! Спасибо, что пополняеете наш Базу Знаний! Теги: {' '.join(tags)}""")
		# Здесь удоли привязку конспекта к юзеру!
		update_user_status(message.from_user, UserStatus.NEW)


def save_content(message: Message):
	'''
	Реализация годная, но лучше просто сохранять file_id - это фича API
	телеграма при которой нам даже не придется скачивать файл к себе.
	Здесь должна происходить запись file_id и тэгов в базу данных.
	'''
	try:
		chat_id = message.chat.id

		file_info = bot.get_file(message.document.file_id)
		downloaded_file = bot.download_file(file_info.file_path)

		src = 'C:/Python/Project/tg_bot/files/received/' + message.document.file_name;
		with open(src, 'wb') as new_file:
			new_file.write(downloaded_file)

		bot.reply_to(message, "Пожалуй, я сохраню это")
	except Exception as e:
		bot.reply_to(message, e)


if RESET_WEBHOOK:
	logger.warning('Removing webhook.')
	bot.remove_webhook()
	time.sleep(1)
	bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
	logger.success('Webhook is setup.')
else:
	logger.info('Webhook will not be changed')
