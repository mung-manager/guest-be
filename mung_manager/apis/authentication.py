from rest_framework_simplejwt.authentication import AuthUser
from rest_framework_simplejwt.authentication import (
    JWTAuthentication as _JWTAuthentication,
)
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import get_md5_hash_password

from mung_manager.common.constants import SYSTEM_CODE
from mung_manager.errors.exceptions import (
    AuthenticationFailedException,
    InvalidTokenException,
)


class JWTAuthentication(_JWTAuthentication):
    """이 클래스는 JWTAuthentication을 상속받아 JWT 토큰을 검증하는 커스텀 클래스입니다.
    로그인 후의 모든 인증 관련 로직은 이 클래스에서 처리됩니다.
    """

    def get_user(self, validated_token: Token) -> AuthUser:
        """유효한 토큰을 검증하고 유저 객체를 반환합니다.

        Args:
            validated_token (Token): JWT Token 객체

        Returns:
            user (AuthUser): 유저 객체
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidTokenException(
                detail=SYSTEM_CODE.message("INVALID_TOKEN_AUTH_USER_IDENTIFICATION"),
                code=SYSTEM_CODE.code("INVALID_TOKEN_AUTH_USER_IDENTIFICATION"),
            )

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailedException(
                detail=SYSTEM_CODE.message("NOT_FOUND_AUTH_USER"),
                code=SYSTEM_CODE.code("NOT_FOUND_AUTH_USER"),
            )

        if user.is_active is False:
            raise AuthenticationFailedException(
                detail=SYSTEM_CODE.message("INACTIVE_AUTH_USER"),
                code=SYSTEM_CODE.code("INACTIVE_AUTH_USER"),
            )

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(api_settings.REVOKE_TOKEN_CLAIM) != get_md5_hash_password(user.password):
                raise AuthenticationFailedException(
                    detail=SYSTEM_CODE.message("REVOKE_TOKEN_AUTH_USER"),
                    code=SYSTEM_CODE.code("REVOKE_TOKEN_AUTH_USER"),
                )

        if user.is_deleted is True and user.deleted_at is not None:
            raise AuthenticationFailedException(
                detail=SYSTEM_CODE.message("DELETED_AUTH_USER"),
                code=SYSTEM_CODE.code("DELETED_AUTH_USER"),
            )

        return user

    def get_validated_token(self, raw_token: bytes) -> Token:
        """이 함수는 토큰을 검증합니다.

        Args:
            raw_token (bytes): 검증할 토큰
        Returns:
            Token: 검증된 토큰 객체
        """
        messages = []

        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError:
                messages.append(AuthToken.token_type)

        raise InvalidTokenException(f"{messages} {SYSTEM_CODE.message('INVALID_TOKEN')}")
