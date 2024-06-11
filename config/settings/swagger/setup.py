import logging

from django.urls import path

logger = logging.getLogger("configuration")


def show_swagger(*args, **kwargs) -> bool:
    from config.settings.swagger.settings import SWAGGER_ENABLED

    if not SWAGGER_ENABLED:
        return False

    try:
        import drf_spectacular  # noqa
        import drf_spectacular_sidecar  # noqa
    except ImportError:
        logger.info("No installation found for: drf_spectacular")
        return False

    return True


class SwaggerSetup:
    @staticmethod
    def do_settings(INSTALLED_APPS):
        _show_swagger: bool = show_swagger()
        logger.info(f"Django Swagger in use: {show_swagger}")

        if not _show_swagger:
            return INSTALLED_APPS

        INSTALLED_APPS += ["drf_spectacular", "drf_spectacular_sidecar"]

        return INSTALLED_APPS

    @staticmethod
    def do_urls(urlpatterns):
        if not show_swagger():
            return urlpatterns

        from drf_spectacular.views import (
            SpectacularJSONAPIView,
            SpectacularSwaggerView,
        )

        return urlpatterns + [
            path(
                "partner/json/docs",
                SpectacularJSONAPIView.as_view(),
                name="schema-json",
            ),
            path(
                "partner/swagger/docs",
                SpectacularSwaggerView.as_view(url_name="schema-json"),
                name="swagger-ui",
            ),
        ]
