import json
from typing import Any, Dict

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

from mung_manager.authentication.services.abstracts import (
    AbstractKakaoLoginFlowService,
    KakaoAccessToken,
    KakaoLoginCredentials,
)
from mung_manager.errors.exceptions import AuthenticationFailedException


class KakaoLoginFlowService(AbstractKakaoLoginFlowService):
    """이 클래스는 카카오 로그인 플로우를 담당합니다.

    Attributes:
        API_URI (str): API URI
        KAKAO_ACCESS_TOKEN_OBTAIN_URL (str): 카카오 토큰 얻기 URL
        KAKAO_USER_INFO_URL (str): 카카오 유저 정보 URL
    """

    API_URI = reverse_lazy("api-auth:kakao-login-callback")

    KAKAO_ACCESS_TOKEN_OBTAIN_URL = "https://kauth.kakao.com/oauth/token"
    KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

    def __init__(self):
        self._credentials = kakao_login_get_credentials()

    def get_token(self, code: str, redirect_uri: str) -> KakaoAccessToken:
        """이 함수는 클라이언트로부터 받은 code와 redirect_uri 이용하여 카카오 토큰 서버로부터 토큰을 얻습니다.

        Args:
            code (str): 클라이언트로부터 받은 code
            redirect_uri (str): 클라이언트로부터 받은 redirect_uri

        Returns:
            KakaoAccessToken: 카카오 토큰
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "client_secret": self._credentials.client_secret,
            "code": code,
        }
        response = requests.post(self.KAKAO_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if response.status_code != 200:
            raise AuthenticationFailedException("Failed to get access token from Kakao.")

        kakao_token = KakaoAccessToken(access_token=response.json()["access_token"])
        return kakao_token

    def get_user_info(self, kakao_token: KakaoAccessToken) -> Dict[str, Any]:
        """이 함수는 카카오 토큰을 이용하여 카카오 유저 정보 서버로부터 유저 정보를 얻습니다.

        Args:
            kakao_token (KakaoAccessToken): 카카오 토큰

        Returns:
            Dict[str, Any]: 카카오 유저 정보
        """
        access_token = kakao_token.access_token
        response = requests.get(
            self.KAKAO_USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            raise AuthenticationFailedException("Failed to get user info from Kakao.")
        return json.loads(response.text)


def kakao_login_get_credentials() -> KakaoLoginCredentials:
    """이 함수는 설정값으로부터 카카오 인증에 필요한 값들을 검증 후 카카오 로그인 인증 객체를 반환합니다.

    Returns:
        KakaoLoginCredentials: 카카오 로그인 인증 객체
    """
    client_id = settings.KAKAO_API_KEY
    client_secret = settings.KAKAO_SECRET_KEY

    if not client_id:
        raise ImproperlyConfigured("KAKAO_API_KEY missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("KAKAO_SECRET_KEY missing in env.")

    credentials = KakaoLoginCredentials(client_id=client_id, client_secret=client_secret)

    return credentials
