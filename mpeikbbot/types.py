import enum


class UserStatus(enum.Enum):
	NEW = 0
	WAIT_CONSPECTUS = 1
	WAIT_TAG = 2
	WAIT_SEARCH = 3


FileID = str
