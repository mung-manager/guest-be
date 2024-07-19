from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status

from mung_manager.commons.base.api_managers import BaseAPIManager
from mung_manager.customers.apis.apis import (
    CustomerCreateReservationAPI,
    CustomerReservationCancelAPI,
    CustomerReservationDetailListAPI,
    CustomerReservationListAPI,
    CustomerTicketCountAPI,
    CustomerTicketPurchaseListAPI,
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
    ErrorInvalidTokenSchema,
    ErrorNotAuthenticatedSchema,
    ErrorPermissionDeniedSchema,
    ErrorUnknownServerSchema, ErrorInvalidParameterFormatSchema,
)
from mung_manager.schemas.errors.customers import (
    ErrorCustomerNotFoundSchema,
    ErrorCustomerPermissionDeniedSchema,
    ErrorCustomerTicketConflictSchema, ErrorCustomerPetNotFoundSchema,
)
from mung_manager.schemas.errors.pet_kindergardens import (
    ErrorPetKindergardenNotFoundSchema,
)
from mung_manager.schemas.errors.reservations import ErrorReservationNotFoundSchema, ErrorInvalidReservedAtSchema, \
    ErrorInvalidEndAtSchema, ErrorInvalidAttendanceTimeSchema
from mung_manager.schemas.errors.tickets import ErrorTicketNotFoundSchema


class CustomerTicketCountAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": CustomerTicketCountAPI.as_view,
    }

    @extend_schema(
        tags=["고객"],
        summary="고객이 소유한 타입별 티켓 개수 조회",
        description="""
        Rogic
            - 고객이 소유한 타입별 티켓 개수 조회 API 입니다.
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
                response=OpenApiTypes.OBJECT, examples=[ErrorPetKindergardenNotFoundSchema]
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["GET"]()(request, *args, **kwargs)


class CustomerReservationAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": CustomerReservationListAPI.as_view,
        "POST": CustomerCreateReservationAPI.as_view,
    }

    @extend_schema(
        tags=["고객"],
        summary="고객의 예약 목록 조회",
        description="""
        Rogic
            - 고객의 예약 목록 조회 API 입니다.
        """,
        responses={
            status.HTTP_200_OK: VIEWS_BY_METHOD["GET"]().cls.OutputSerializer,
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

    @extend_schema(
        tags=["고객"],
        summary="고객의 반려동물 유치원 예약하기",
        description="""
        Rogic
            - 고객의 반려동물 유치원 예약하기 API 입니다.
        """,
        responses={
            status.HTTP_200_OK: VIEWS_BY_METHOD["POST"]().cls.OutputSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorInvalidParameterFormatSchema,
                    ErrorInvalidReservedAtSchema,
                    ErrorInvalidEndAtSchema,
                    ErrorInvalidAttendanceTimeSchema,
                    ErrorCustomerTicketConflictSchema,
                ],
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
                    ErrorCustomerPetNotFoundSchema,
                    ErrorCustomerNotFoundSchema,
                    ErrorTicketNotFoundSchema,
                ],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["POST"]()(request, *args, **kwargs)


class CustomerReservationDetailListAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": CustomerReservationDetailListAPI.as_view,
    }

    @extend_schema(
        tags=["고객"],
        summary="고객의 상세 예약 목록 조회",
        description="""
        Rogic
            - 고객의 상세 예약 목록 조회 API 입니다.
        """,
        parameters=[VIEWS_BY_METHOD["GET"]().cls.FilterSerializer],
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
                examples=[ErrorPermissionDeniedSchema],
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


class CustomerTicketPurchaseListAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": CustomerTicketPurchaseListAPI.as_view,
    }

    @extend_schema(
        tags=["고객"],
        summary="고객의 이용권 구매 내역 목록 조회",
        description="""
        Rogic
            - 고객의 이용권 구매 내역 목록 조회 API 입니다.
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
                examples=[ErrorPermissionDeniedSchema],
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


class CustomerReservationCancelAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "DELETE": CustomerReservationCancelAPI.as_view,
    }

    @extend_schema(
        tags=["고객"],
        summary="고객의 반려동물 유치원 예약 취소",
        description="""
        Rogic
            - 고객의 반려동물 유치원 예약 취소 API 입니다.
        """,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiTypes.NONE,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    ErrorCustomerTicketConflictSchema,
                ],
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
                examples=[
                    ErrorReservationNotFoundSchema,
                    ErrorPetKindergardenNotFoundSchema,
                ],
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=OpenApiTypes.OBJECT, examples=[ErrorUnknownServerSchema]
            ),
        },
    )
    def delete(self, request, *args, **kwargs):
        return self.VIEWS_BY_METHOD["DELETE"]()(request, *args, **kwargs)
