from django.conf import settings
import warnings

if getattr(settings, 'DJANGO_MARKUP_IGNORE_WARNINGS', False):
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='markup_deprecated')
