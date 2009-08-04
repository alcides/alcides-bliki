from settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = relative('db/prod.db') # Or path to database file if using sqlite3.
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''             # empty -> localhost
DATABASE_PORT = ''             # empty -> default

# staticgenerator

WEB_ROOT = relative('public/')

STATIC_GENERATOR_URLS = (
    r'^/$',
    r'^/(?!(admin|feeds))(?P<slug>\S+)$',
)

MIDDLEWARE_CLASSES = tuple(list(MIDDLEWARE_CLASSES) + [
	'staticgenerator.middleware.StaticGeneratorMiddleware'
])