import os

from settings import *


def load_secret_environment(path):
	"""Load deployment-only API credentials without committing them."""
	try:
		with open(path, encoding="utf-8") as secret_file:
			for line in secret_file:
				key, separator, value = line.strip().partition("=")
				if key and separator:
					os.environ.setdefault(key, value)
	except FileNotFoundError:
		pass


load_secret_environment("/home/alcides/.config/wiki_alcidesfonseca_com/lastfm.env")
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': relative('db/prod.db')
    }
}

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda x: False,
}
ALLOWED_HOSTS = ['alcidesfonseca.com', 'localhost', 'wiki.alcidesfonseca.com']
