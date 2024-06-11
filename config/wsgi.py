import os

from django.core.wsgi import get_wsgi_application

from config.django.base import SERVER_ENV

os.environ.setdefault("DJANGO_SETTINGS_MODULE", SERVER_ENV)

application = get_wsgi_application()
