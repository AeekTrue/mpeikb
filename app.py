import flask
import telebot.types

from config import *
from mpeikbbot import bot

app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'HEAD'])
def index():
	return ''


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
	if flask.request.headers.get('content-type') == 'application/json':
		json_string = flask.request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_updates([update])
		return ''
	else:
		flask.abort(403)
