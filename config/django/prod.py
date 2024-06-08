from config.env import env
from config.django.base import *  # noqa

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("PROD_POSTGRESQL_DATABASE"),
        "USER": env("PROD_POSTGRESQL_USER"),
        "PASSWORD": env("PROD_POSTGRESQL_PASSWORD"),
        "HOST": env("PORD_POSTGRESQL_HOST"),
        "PORT": env("PROD_POSTGRESQL_PORT"),
        "CONN_MAX_AGE": 60,
    }
}


CORS_ALLOW_ALL_ORIGINS = False
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])

CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=True)
