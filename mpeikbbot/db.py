import psycopg2
from psycopg2.extras import NamedTupleCursor
import config

conn = psycopg2.connect(dbname=config.DB_NAME, user=config.DB_LOGIN,
						password=config.DB_PASSWORD, host=config.DB_HOST)
cursor = conn.cursor(cursor_factory=NamedTupleCursor)
conn.autocommit = True
