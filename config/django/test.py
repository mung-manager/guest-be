import platform

from config.django.base import *  # noqa
from config.env import env

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("TEST_POSTGRESQL_DATABASE", default="mung_manager"),
        "USER": env("TEST_POSTGRESQL_USER", default="postgres"),
        "PASSWORD": env("TEST_POSTGRESQL_PASSWORD", default="password"),
        "HOST": env("TEST_POSTGRESQL_HOST", default="postgres_db"),
        "PORT": env("TEST_POSTGRESQL_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}


if platform.system() == "Darwin":
    GEOS_LIBRARY_PATH = env.str("GEOS_LIBRARY_PATH")
    GDAL_LIBRARY_PATH = env.str("GDAL_LIBRARY_PATH")
