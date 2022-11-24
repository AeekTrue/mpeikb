from loguru import logger
import sys

logger.add(sys.stderr, level="DEBUG", format='[{time}] [{level}] {message}')
