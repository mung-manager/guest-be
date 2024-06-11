from config.env import env

SWAGGER_ENABLED = env.bool("SWAGGER_ENABLED", default=True)

SPECTACULAR_SETTINGS = {
    "TITLE": "멍매니저 손님 API 문서",
    "CONTACT": {
        "name": "김동욱",
        "url": "https://github.com/DongwookKim0823",
        "email": "ehddnr7355@gmail.com",
    },
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SWAGGER_UI_SETTINGS": {
        "dom_id": "#swagger-ui",
        "layout": "BaseLayout",
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "filter": True,
        "defaultModelsExpandDepth": -1,
    },
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "DISABLE_ERRORS": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
}
