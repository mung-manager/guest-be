from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status

from mung_manager.commons.base.api_managers import BaseAPIManager
from mung_manager.pet_kindergardens.apis.apis import (
    PetKindergardenListAPI,
    PetKindergardenSelectionAPI,
)
from mung_manager.schemas.errors.authentications import (
    ErrorAuthenticationPasswordChangedSchema,
    ErrorAuthenticationUserDeletedSchema,
    ErrorAuthenticationUserInactiveSchema,
    ErrorAuthenticationUserNotFoundSchema,
    ErrorAuthorizationHeaderSchema,
    ErrorTokenIdentificationSchema,
)
from mung_manager.schemas.errors.commons import (
    ErrorAuthenticationFailedSchema,
    ErrorInvalidParameterFormatSchema,
    ErrorInvalidTokenSchema,
    ErrorNotAuthenticatedSchema,
    ErrorPermissionDeniedSchema,
    ErrorUnknownServerSchema,
)
from mung_manager.schemas.errors.pet_kindergardens import (
    ErrorPetKindergardenNotFoundSchema,
)


class PetkindergardenListAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": PetKindergardenListAPI.as_view,
    }

    @extend_schema(
        tags=["반려동물 유치원"],
        summary="반려동물 유치원 목록 조회",
        description="""
        Rogic
            - 유저가 선택할 수 있는 유치원 목록을 조회합니다.
        """,
        responses={
            status.HTTP_200_OK: VIEWS_BY_METHOD["GET"]().cls.OutputSerializer,
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorAuthenticationFailedSchema,
                    ErrorNotAuthenticatedSchema,
                    ErrorInvalidTokenSchema,
                    ErrorAuthorizationHeaderSchema,
                    ErrorAuthenticationPasswordChangedSchema,
                    ErrorAuthenticationUserDeletedSchema,
                    ErrorAuthenticationUserInactiveSchema,
                    ErrorAuthenticationUserNotFoundSchema,
                    ErrorTokenIdentificationSchema,
                ],
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorPermissionDeniedSchema]
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)


class PetKindergardenSelectionAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "POST": PetKindergardenSelectionAPI.as_view,
    }

    @extend_schema(
        tags=["반려동물 유치원"],
        summary="반려동물 유치원 선택",
        description="""
            Rogic
                - 유저가 예약할 반려견 유치원을 선택합니다.
            """,
        request=VIEWS_BY_METHOD["POST"]().cls.InputSerializer,
        responses={
            status.HTTP_200_OK: VIEWS_BY_METHOD["POST"]().cls.OutputSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[ErrorInvalidParameterFormatSchema],
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorAuthenticationFailedSchema,
                    ErrorNotAuthenticatedSchema,
                    ErrorInvalidTokenSchema,
                    ErrorAuthorizationHeaderSchema,
                    ErrorAuthenticationPasswordChangedSchema,
                    ErrorAuthenticationUserDeletedSchema,
                    ErrorAuthenticationUserInactiveSchema,
                    ErrorAuthenticationUserNotFoundSchema,
                    ErrorTokenIdentificationSchema,
                ],
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[ErrorPermissionDeniedSchema],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[ErrorPetKindergardenNotFoundSchema],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[ErrorUnknownServerSchema],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["POST"]()(request, *args, **kwargs)
