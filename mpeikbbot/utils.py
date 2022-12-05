import re
from logger import logger

tag_pattern = r'[а-яА-ЯёЁa-zA-Z0-9+]'
p = re.compile(tag_pattern)


def parse_tags(text: str):
	tags = text.lower().replace('_', '').lstrip('#').split()
	return set([tag for tag in tags if p.match(tag)])
