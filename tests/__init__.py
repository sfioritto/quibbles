from django.core.management import setup_environ
from webapp import settings
from conf import EMAIL
import os

#run tests as if in the email directory, (for lamson)
os.chdir(EMAIL)
os.environ['DJANGO_SETTINGS_MODULE'] = 'webapp.settings'

#So we can access django models, views, etc.
setup_environ(settings)
