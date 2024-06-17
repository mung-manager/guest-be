from django.urls import path

from mung_manager.authentications.apis.api_managers import (
    JWTRefreshAPIManager,
    KakaoLoginAPIManager,
)

urlpatterns = [
    # oauth
    path(
        "/kakao/callback",
        KakaoLoginAPIManager.as_view(),
        name="kakao-login-callback",
    ),
    # auth
    path(
        "/jwt/refresh",
        JWTRefreshAPIManager.as_view(),
        name="jwt-refresh",
    ),
]
