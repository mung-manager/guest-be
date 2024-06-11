import os

from django.core.asgi import get_asgi_application

from config.django.base import SERVER_ENV

os.environ.setdefault("DJANGO_SETTINGS_MODULE", SERVER_ENV)

application = get_asgi_application()
