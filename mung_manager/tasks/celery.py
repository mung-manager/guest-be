from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from config.django.base import SERVER_ENV

os.environ.setdefault("DJANGO_SETTINGS_MODULE", SERVER_ENV)

app = Celery("mung_manager")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
