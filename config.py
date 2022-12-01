import os
import dotenv

if os.path.exists('.env'):
	dotenv.load_dotenv()

TOKEN = os.environ['TELEBOT_TOKEN']
ADMIN_ID = int(os.environ['TELEBOT_ADMIN_ID'])

WEBHOOK = os.environ['TELEBOT_WEBHOOK']
WEBHOOK_URL_BASE = f'https://{WEBHOOK}'
WEBHOOK_URL_PATH = f'/{TOKEN}/'
RESET_WEBHOOK = int(os.environ['RESET_WEBHOOK'])

DB_NAME = os.environ['DB_NAME']
DB_HOST = os.environ['DB_HOST']
DB_LOGIN = os.environ['DB_LOGIN']
DB_PASSWORD = os.environ['DB_PASSWORD']
