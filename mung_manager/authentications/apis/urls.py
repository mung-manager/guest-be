from django.urls import path

from mung_manager.authentications.apis.api_managers import KakaoLoginAPIManager

urlpatterns = [
    # oauth
    path(
        "/kakao/callback",
        KakaoLoginAPIManager.as_view(),
        name="kakao-login-callback",
    ),
]
