#!/usr/bin/python3

import sys
import os
INTERP = "/home/alcides/sites/wiki_alcidesfonseca_com/.venv/bin/python3"
#INTERP is present twice so that the new Python interpreter knows the actual executable path
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

import pathlib

p = pathlib.Path(os.path.dirname(__file__))

sys.path.append(p / ".venv" / "lib" / "python3.8" / "site-packages")

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings-prod'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

