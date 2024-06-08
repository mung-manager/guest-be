from config.django.base import SERVER_ENV
import logging


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "django.server": {
            "format": (
                "[%(asctime)s] %(levelname)s [PID: %(process)d - %(processName)s] "
                "| [TID: %(thread)d - %(threadName)s] %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "django.server",
        },
    },
}


if SERVER_ENV == "config.django.local":
    LOGGING["loggers"] = {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    }

logger = logging.getLogger("django")
