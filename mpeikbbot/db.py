from typing import List

import psycopg2
from psycopg2.extras import NamedTupleCursor
from telebot.types import User

import config
from logger import logger
from .types import UserStatus, FileID

conn = psycopg2.connect(dbname=config.DB_NAME, user=config.DB_LOGIN,
						password=config.DB_PASSWORD, host=config.DB_HOST)
cursor = conn.cursor(cursor_factory=NamedTupleCursor)
conn.autocommit = True


def add_user(user: User):
	logger.info(f'New user {user.id}')
	cursor.execute(f'INSERT INTO status(user_id, status_id) values ({user.id}, 0)')


def get_or_set_user_status(user: User) -> UserStatus:
	"""Возвращает статус в котором находится пользователь. По умолчанию NEW"""
	cursor.execute(f'SELECT status_id FROM status WHERE user_id={user.id}')
	record = cursor.fetchone()
	if record is None:
		status = UserStatus(0)
		add_user(user)
	else:
		status = UserStatus(record.status_id)
	logger.debug(status)
	return status


def update_user_status(user: User, status: UserStatus):
	user.status = status
	cursor.execute(f'UPDATE status SET status_id={status.value} WHERE user_id={user.id}')
	logger.debug(f'New US {status}')


def get_all_tags():
	cursor.execute('SELECT name FROM tag')
	return cursor.fetchall()


def create_tag(tag_name, description=''):
	"""Записывает тег в базу данных, если ранее его там не было. возвращает ID тега"""
	cursor.execute(f"SELECT id FROM tag WHERE name='{tag_name}'")
	result = cursor.fetchone()
	if result is None:
		logger.info(f'Create new tag {tag_name}')
		cursor.execute(f"INSERT INTO tag(name, description) VALUES ('{tag_name}', '{description}')")
		cursor.execute(f"SELECT currval('tag_id_seq')")
		tag_id = cursor.fetchone().currval
		return tag_id
	else:
		return result.id


def register_new_file_id(user_id: int, file_id: FileID, file_type: str):
	"""Закрепляет за пользователем только что полученный от него файл.
	"""
	logger.debug('Did user created conspectus before?...')
	cursor.execute(f'SELECT file_id FROM user_conspectus WHERE user_id={user_id}')
	result = cursor.fetchone()
	logger.debug(result)
	if result is None:
		logger.debug("He didn't. Insert")
		cursor.execute(
			f"INSERT INTO user_conspectus(user_id, file_id, file_type) VALUES ({user_id}, '{file_id}', '{file_type}')")
	else:
		logger.debug("He did. Update")
		cursor.execute(
			f"UPDATE user_conspectus SET file_id='{file_id}', file_type='{file_type}' WHERE user_id={user_id}")
	logger.info(f'Register new conspectus for {user_id}')


def get_current_file_for_user(user_id: int):
	"""Возвращает файл, закрепленный за пользователем на данный момент"""
	cursor.execute(f'SELECT file_id, file_type FROM user_conspectus WHERE user_id={user_id}')
	result = cursor.fetchone()
	if result is None:
		return ''
	else:
		return result


def add_tag_to_conspectus(conspectus_id, tag_id):
	cursor.execute(f"INSERT INTO conspect_tag(conspect_id, tag_id) VALUES ({conspectus_id}, {tag_id})")


def create_conspectus(file_id: FileID, file_type: str, tags):
	logger.debug('create conspectus...')
	cursor.execute(f"INSERT INTO conspect(file_id, file_type) VALUES ('{file_id}', '{file_type}')")
	logger.debug('get its ID')
	cursor.execute(f"SELECT currval('conspect_id_seq')")
	conspectus_id = cursor.fetchone().currval
	logger.debug(f'Conspectus ID = {conspectus_id}')
	logger.debug(f'{tags = }')
	for tag in tags:
		cursor.execute(f"SELECT id FROM tag WHERE name='{tag}'")
		tag_id = cursor.fetchone()
		if tag_id is None:
			tag_id = create_tag(tag)
		else:
			logger.debug(f'Tag already exists.')
			tag_id = tag_id.id
		add_tag_to_conspectus(conspectus_id, tag_id)
		logger.debug(f'Tag {tag} has id {tag_id}')


def find_conspectuses(tags):
	conspectuses = set()
	for tag in tags:
		cursor.execute(
			f"SELECT c.file_id, c.rating, c.file_type from conspect_tag ct left join tag t on t.id = ct.tag_id left join conspect c on c.id = ct.conspect_id WHERE t.name='{tag}'")
		conspectuses.update(cursor.fetchall())
	logger.debug(f'found {len(conspectuses)}')
	logger.debug(conspectuses)
	return conspectuses
