from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from mung_manager.authentications.apis.apis import JWTRefreshAPI, KakaoLoginAPI
from mung_manager.commons.base.api_managers import BaseAPIManager
from mung_manager.schemas.errors.authentications import (
    ErrorAuthenticationUserInactiveSchema,
    ErrorKakaoAccessTokenFailedSchema,
    ErrorKakaoPhoneNumberNotAuthenticatedSchema,
    ErrorKakaoUserInfoFailedSchema,
    ErrorOauthErrorSchema,
)
from mung_manager.schemas.errors.commons import (
    ErrorInvalidParameterFormatSchema,
    ErrorInvalidTokenSchema,
    ErrorUnknownServerSchema,
)


class KakaoLoginAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": KakaoLoginAPI.as_view,
    }

    @extend_schema(
        tags=["인증"],
        summary="카카오 로그인 콜백",
        description="""
        Rogic
            - 카카오 로그인 콜백 API 입니다.
            - 카카오 로그인을 완료하면, 카카오에서 전달받은 정보를 토대로 앱 유저를 생성합니다.
            - 액세스 토큰과 리프레쉬 토큰을 발급합니다. (엑세스 토큰 3시간, 리프레쉬 토큰 2주)
        """,
        parameters=[VIEWS_BY_METHOD["GET"]().cls.InputSerializer],
        responses={
            status.HTTP_200_OK: VIEWS_BY_METHOD["GET"]().cls.OutputSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorInvalidParameterFormatSchema]
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorOauthErrorSchema,
                    ErrorKakaoAccessTokenFailedSchema,
                    ErrorKakaoUserInfoFailedSchema,
                    ErrorKakaoPhoneNumberNotAuthenticatedSchema,
                    ErrorAuthenticationUserInactiveSchema,
                ],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)


class JWTRefreshAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "POST": JWTRefreshAPI.as_view,
    }

    @extend_schema(
        tags=["인증"],
        summary="인증 토큰 재발급",
        description="""
        Rogic
            - 리프레쉬 토큰을 통해 액세스 토큰을 재발급합니다. (액세스 토큰 3시간)
        """,
        request=TokenRefreshSerializer,
        responses={
            status.HTTP_200_OK: VIEWS_BY_METHOD["POST"]().cls.OutputSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorInvalidParameterFormatSchema]
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorOauthErrorSchema, ErrorInvalidTokenSchema]
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["POST"]()(request, *args, **kwargs)
