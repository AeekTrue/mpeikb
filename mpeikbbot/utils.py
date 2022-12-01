from logger import logger
from telebot.types import User
from .db import cursor
import enum


class UserStatus(enum.Enum):
	NEW = 0
	WAIT_CONSPECTUS = 1
	WAIT_TAG = 2
	WAIT_SEARCH = 3


def add_user(user: User):
	logger.info(f'New user {user.id}')
	cursor.execute(f'INSERT INTO status(user_id, status_id) values ({user.id}, 0)')


def update_user_status(user: User, status: UserStatus):
	user.status = status
	cursor.execute(f'UPDATE status SET status_id={status.value} WHERE user_id={user.id}')


def get_or_set_user_status(user: User) -> UserStatus:
	cursor.execute(f'SELECT status_id FROM status WHERE user_id={user.id}')
	record = cursor.fetchone()
	if record is None:
		status = UserStatus(0)
		add_user(user)
	else:
		status = UserStatus(record.status_id)
	logger.debug(status)
	return status
