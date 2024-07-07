from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status

from mung_manager.commons.base.api_managers import BaseAPIManager
from mung_manager.customers.apis.apis import (
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
    ErrorUnknownServerSchema,
)
from mung_manager.schemas.errors.customers import (
    ErrorCustomerNotFoundSchema,
    ErrorCustomerPermissionDeniedSchema,
)
from mung_manager.schemas.errors.pet_kindergardens import (
    ErrorPetKindergardenNotFoundSchema,
)


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


class CustomerReservationListAPIManager(BaseAPIManager):
    VIEWS_BY_METHOD = {
        "GET": CustomerReservationListAPI.as_view,
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
