from config.env import env
from config.django.base import SERVER_ENV
import urllib

# Celery
CELERY_DEFAULT_QUEUE = "guest_default"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Seoul"
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"

if SERVER_ENV in ["config.django.local", "config.django.test"]:
    CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/10")
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "visibility_timeout": 3600,
    }
else:
    AWS_SQS_ACCESS_KEY_ID = env("AWS_SQS_ACCESS_KEY_ID", default=None)
    AWS_SQS_SECRET_ACCESS_KEY = env("AWS_SQS_SECRET_ACCESS_KEY", default=None)
    aws_sqs_access_key_id = urllib.parse.quote(f"{AWS_SQS_ACCESS_KEY_ID}", safe="")
    aws_sqs_secret_access_key = urllib.parse.quote(f"{AWS_SQS_SECRET_ACCESS_KEY}", safe="")
    CELERY_BROKER_URL = f"sqs://{aws_sqs_access_key_id}:{aws_sqs_secret_access_key}@"
    if SERVER_ENV == "config.django.prod":
        AWS_SQS_CELERY_URL = env.str("AWS_PROD_SQS_CELERY_URL")
    else:
        AWS_SQS_CELERY_URL = env.str("AWS_DEV_SQS_CELERY_URL")
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "region": "ap-northeast-2",
        "predefined_queues": {
            "guest_default": {
                "url": AWS_SQS_CELERY_URL,
            },
        },
        "visibility_timeout": 3600,
        "polling_interval": 60,
        "CELERYD_PREFETCH_MULTIPLIER": 0,
    }
