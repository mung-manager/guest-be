import os

from config.env import APPS_DIR, BASE_DIR, env

SERVER_ENV = os.environ.get("DJANGO_SETTINGS_MODULE", "config.django.base")

env.read_env(os.path.join(BASE_DIR, ".env.guest"))

SECRET_KEY = "test"

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ==================================================================== #
#                     설치된 앱, 사용하는 앱 config                         #
# ==================================================================== #
LOCAL_APPS = [
    "mung_manager.commons.apps.CommonConfig",
    "mung_manager.schemas.apps.SchemasConfig",
    "mung_manager.authentications.apps.AuthenticationConfig",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "django_celery_results",
    "django_celery_beat",
    "concurrency",
]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.root_urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(APPS_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


AUTH_USER_MODEL = "authentications.User"

APP_DOMAIN = env("APP_DOMAIN", default="http://localhost:8000")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ==================================================================== #
#                   Internationalization                               #
# ==================================================================== #
LANGUAGE_CODE = "en-us"  # 언어 - 국가 설정

TIME_ZONE = "Asia/Seoul"  # 시간대 설정

USE_I18N = False  # 국제화

USE_TZ = False  # 장고 시간대 사용 여부

# ==================================================================== #
#                       DRF config                                     #
# ==================================================================== #
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("mung_manager.apis.render.CamelCaseJSONRenderer",),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
    ),
    "EXCEPTION_HANDLER": "mung_manager.errors.exception_handler.default_exception_handler",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_SCHEMA_CLASS": "config.settings.swagger.openapi.AutoSchema",
}


from config.settings.cors import *  # noqa
from config.settings.files_and_storages import *  # noqa
from config.settings.sentry import *  # noqa
from config.settings.jwt import *  # noqa
from config.settings.logging import *  # noqa
from config.settings.oauth import *  # noqa

from config.settings.debug_toolbar.settings import *  # noqa
from config.settings.debug_toolbar.setup import DebugToolbarSetup  # noqa
from config.settings.swagger.settings import *  # noqa
from config.settings.swagger.setup import SwaggerSetup  # noqa

INSTALLED_APPS, MIDDLEWARE = DebugToolbarSetup.do_settings(INSTALLED_APPS, MIDDLEWARE)
INSTALLED_APPS = SwaggerSetup.do_settings(INSTALLED_APPS)
