import os

from frinat.settings.common import *

STAGE_BASE = os.path.dirname(os.path.dirname(__file__))

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = '{dbname}'
DATABASE_USER = DATABASE_NAME
DATABASE_PASSWORD = '{dbpass}'

MEDIA_ROOT = os.path.join(STAGE_BASE, 'static')
