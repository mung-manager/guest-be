from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from attrs import define

from mung_manager.authentications.models import User
from mung_manager.errors.exceptions import NotImplementedException


@define
class KakaoLoginCredentials:
    client_id: str
    client_secret: str


@define
class KakaoAccessToken:
    access_token: str


class AbstractAuthService(ABC):
    @abstractmethod
    def generate_token(self, user: User) -> Tuple[str, str]:
        raise NotImplementedException()

    @abstractmethod
    def authenticate_user(self, user: User) -> User:
        raise NotImplementedException()


class AbstractKakaoLoginFlowService(ABC):
    @abstractmethod
    def get_token(self, code: str, redirect_uri: str) -> KakaoAccessToken:
        raise NotImplementedException()

    @abstractmethod
    def get_user_info(self, kakao_token: KakaoAccessToken) -> Dict[str, Any]:
        raise NotImplementedException()


class AbstractUserService(ABC):
    @abstractmethod
    def create_kakao_user(
        self,
        email: str,
        name: str,
        social_id: str,
        phone_number: str,
        birth: object,
        gender: str,
        social_provider: int,
        has_phone_number: bool,
    ) -> User:
        raise NotImplementedException()
