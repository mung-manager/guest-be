from kombu.utils.url import safequote


from config.env import env


# Credentials
AWS_ACCESS_KEY_ID = env("AWS_SQS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = env("AWS_SQS_SECRET_ACCESS_KEY", default=None)
AWS_REGION = env("AWS_SQS_REGION_NAME", default=None)
aws_access_key_id = safequote(AWS_ACCESS_KEY_ID)
aws_secret_access_key = safequote(AWS_SECRET_ACCESS_KEY)


# Celery
CELERY_DEFAULT_QUEUE = "sqs"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Seoul"
CELERY_TASK_SOFT_TIME_LIMIT = 20  # seconds
CELERY_TASK_TIME_LIMIT = 30  # seconds
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_QUEUE = "sqs"
CELERY_RESULT_BACKEND = "django-db"


CELERY_BROKER_URL = f"sqs://{aws_access_key_id}:{aws_secret_access_key}@"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": AWS_REGION,
    "visibility_timeout": 3600,
    "polling_interval": 60,
    "CELERYD_PREFETCH_MULTIPLIER": 0,
}
