from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status

from mung_manager.commons.base.api_managers import BaseAPIManager
from mung_manager.reservations.apis.apis import (
    ReservationCustomerPetListAPI,
    ReservationCustomerTicketListAPI,
    ReservationCustomerTicketTypeDetailAPI,
    ReservationPetKindergardenAvailableDatesAPI,
    ReservationCustomerTicketTypesAPI,
    ReservationTicketCheckExpirationAPI,
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
from mung_manager.schemas.errors.customers import (
    ErrorCustomerNotFoundSchema,
    ErrorCustomerPermissionDeniedSchema,
)
from mung_manager.schemas.errors.pet_kindergardens import (
    ErrorPetKindergardenNotFoundSchema,
)
from mung_manager.schemas.errors.reservations import ErrorReservationNotFoundSchema
from mung_manager.schemas.errors.tickets import ErrorTicketNotFoundSchema


class ReservationCustomerPetListAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": ReservationCustomerPetListAPI.as_view,
    }

    @extend_schema(
        tags=["예약"],
        summary="고객의 반려견 목록 조회",
        description="""
        Rogic
            - 반려동물 유치원에 등록된 고객의 반려견 목록을 조회합니다.
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
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorPermissionDeniedSchema,
                    ErrorCustomerPermissionDeniedSchema,
                ],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorPetKindergardenNotFoundSchema,
                    ErrorCustomerNotFoundSchema,
                ],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)


class ReservationCustomerTicketTypesAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": ReservationCustomerTicketTypesAPI.as_view,
    }

    @extend_schema(
        tags=["예약"],
        summary="고객의 잔여 티켓 타입 목록 조회",
        description="""
        Rogic
            - 반려동물 유치원에 등록된 고객의 잔여 티켓 타입 목록을 조회합니다.
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
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorPermissionDeniedSchema,
                    ErrorCustomerPermissionDeniedSchema,
                ],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorPetKindergardenNotFoundSchema,
                    ErrorCustomerNotFoundSchema,
                ],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)


class ReservationCustomerTicketTypeDetailAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": ReservationCustomerTicketTypeDetailAPI.as_view,
    }

    @extend_schema(
        tags=["예약"],
        summary="선택한 티켓 타입의 상세 정보 조회",
        description="""
        Rogic
            - 선택한 티켓 타입의 상세 정보를 조회합니다.
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
                examples=[
                    ErrorPermissionDeniedSchema,
                    ErrorCustomerPermissionDeniedSchema,
                ],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorPetKindergardenNotFoundSchema,
                    ErrorCustomerNotFoundSchema,
                ],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)


class ReservationTicketCheckExpirationAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": ReservationTicketCheckExpirationAPI.as_view,
    }

    @extend_schema(
        tags=["예약"],
        summary="예약에 사용된 티켓들의 만료일과 만료 여부 조회",
        description="""
        Rogic
            - 예약 취소를 위해 예약에 사용된 티켓들의 만료일과 만료 여부를 조회합니다.
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
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorPermissionDeniedSchema,
                ],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[ErrorPetKindergardenNotFoundSchema, ErrorReservationNotFoundSchema],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)


class ReservationPetKindergardenAvailableDatesAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": ReservationPetKindergardenAvailableDatesAPI.as_view,
    }

    @extend_schema(
        tags=["예약"],
        summary="예약 가능한 날짜 목록 조회",
        description="""
        Rogic
            - 선택한 티켓 타입으로 해당 반려동물 유치원의 예약 가능한 날짜 목록을 조회합니다.
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
                examples=[
                    ErrorPermissionDeniedSchema,
                    ErrorCustomerPermissionDeniedSchema,
                ],
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorTicketNotFoundSchema,
                    ErrorPetKindergardenNotFoundSchema,
                ],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)
