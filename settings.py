import os


def relative(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

DEBUG = True
ALLOWED_HOSTS = []


ADMINS = (
    ('Alcides', 'me@alcidesfonseca.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': relative('db/dev.db')
    }
}

SECRET_KEY = 'm-@7tq)&u2u(qzw&y@92l!ady4+$=1-rvj0y@n#-tlp!6pw1)c'


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Lisbon'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = relative('public/media/')
MEDIA_URL = '/public/media/'
STATIC_ROOT = relative('public/static/')
STATIC_URL = '/static/'

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'markup_deprecated',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'markitup',
    'wiki',
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        "DIRS": ["wiki/templates/"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
]


WSGI_APPLICATION = 'wiki.wsgi.application'



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

MARKITUP_FILTER = ('django_markwhat.templatetags.markup.textile', {})
