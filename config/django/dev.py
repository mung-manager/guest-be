from config.env import env
from config.django.base import *  # noqa

SECRET_KEY = env("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DEV_POSTGRESQL_DATABASE"),
        "USER": env("DEV_POSTGRESQL_USER"),
        "PASSWORD": env("DEV_POSTGRESQL_PASSWORD"),
        "HOST": env("DEV_POSTGRESQL_HOST"),
        "PORT": env("DEV_POSTGRESQL_PORT"),
        "CONN_MAX_AGE": 60,
    }
}

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=True)
