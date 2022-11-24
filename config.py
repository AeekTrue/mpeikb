import os
import dotenv

if os.path.exists('.env'):
    dotenv.load_dotenv()

TOKEN = os.environ['TELEBOT_TOKEN']
ADMIN_ID = int(os.environ['TELEBOT_ADMIN_ID'])
WEBHOOK = os.environ['TELEBOT_WEBHOOK']

WEBHOOK_URL_BASE = f'https://{WEBHOOK}'
WEBHOOK_URL_PATH = f'/{TOKEN}/'
