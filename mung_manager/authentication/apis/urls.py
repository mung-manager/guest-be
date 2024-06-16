from django.urls import path

from mung_manager.authentication.apis.api_managers import KakaoLoginAPIManager

urlpatterns = [
    # oauth
    path(
        "/kakao/callback",
        KakaoLoginAPIManager.as_view(),
        name="kakao-login-callback",
    ),
]
