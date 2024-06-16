from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path


urlpatterns = [
    path(
        "guest/api/v1/auth",
        include(
            (
                "mung_manager.authentication.apis.urls",
                "api-authentication",
            )
        ),
    ),
]

from config.settings.debug_toolbar.setup import DebugToolbarSetup  # noqa
from config.settings.swagger.setup import SwaggerSetup  # noqa

urlpatterns = DebugToolbarSetup.do_urls(urlpatterns)
urlpatterns = SwaggerSetup.do_urls(urlpatterns)

# Static/Media File Root (CSS, JavaScript, Images)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
