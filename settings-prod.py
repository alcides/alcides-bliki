from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': relative('db/prod.db')
    }
}

ALLOWED_HOSTS = ['alcidesfonseca.com', 'localhost']