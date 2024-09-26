from config.env import env
from config.django.base import SERVER_ENV

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

if SERVER_ENV == "config.django.prod":
    BASE_BACKEND_URL = env.str("DJANGO_PROD_BASE_BACKEND_URL", default="http://localhost:8000")
else:
    BASE_BACKEND_URL = env.str("DJANGO_DEV_BASE_BACKEND_URL", default="http://localhost:8000")

BASE_FRONTEND_URL = env.str("DJANGO_FRONTEND_URL", default="http://localhost:3000")
CORS_ORIGIN_WHITELIST = env.list("DJANGO_CORS_ORIGIN_WHITELIST", default=[BASE_FRONTEND_URL])

CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST
