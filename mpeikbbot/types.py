import enum
from collections import namedtuple


class UserStatus(enum.Enum):
	NEW = 0
	WAIT_CONSPECTUS = 1
	WAIT_TAG = 2
	WAIT_SEARCH = 3


FileID = str

Conspectus = namedtuple('Conspectus', ['id', 'file_id', 'rating', 'common_tags', 'file_type', 'conspectus_tags'])
