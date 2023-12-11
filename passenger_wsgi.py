#!/usr/bin/python3

import os
import sys
import pathlib

p = pathlib.Path(os.path.dirname(__file__))

sys.path.append(p / ".venv" / "lib" / "python3.8" / "site-packages")

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings-prod'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

