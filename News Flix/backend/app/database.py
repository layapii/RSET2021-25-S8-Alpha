#to communicate with postgresql

import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings # for access to env vars(db config)

# db connection using postgres driver to use sql queries. No need if using sqlalchemy
while True:
    try:
        conn = psycopg2.connect(host=f'{settings.database_hostname}', database=f'{settings.database_name}', user=f'{settings.database_username}', password=f'{settings.database_password}', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB connection successful!")
        break
    except Exception as e:
        print("DB connection failed:\n ", e)
        time.sleep(10)
