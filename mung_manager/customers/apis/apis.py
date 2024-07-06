from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthMixin
from mung_manager.apis.pagination import LimitOffsetPagination, get_paginated_data
from mung_manager.commons.base.serializers import BaseSerializer
from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import (
    get_object_or_not_found,
    get_object_or_permission_denied,
)
from mung_manager.commons.utils import inline_serializer
from mung_manager.customers.containers import CustomerContainer
from mung_manager.reservations.containers import ReservationContainer


class CustomerTicketCountAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        time_count = serializers.IntegerField(label="시간권 예약")
        all_day_count = serializers.IntegerField(label="종일권 예약")
        hotel_count = serializers.IntegerField(label="호텔권 예약")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_ticket_selector = CustomerContainer.customer_ticket_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden_id = request.pet_kindergarden.id
        customer = get_object_or_permission_denied(
            self._customer_selector.get_by_user_and_pet_kindergarden_id_for_active_customer(user, pet_kindergarden_id),
            msg=SYSTEM_CODE.message("INACTIVE_CUSTOMER"),
            code=SYSTEM_CODE.code("INACTIVE_CUSTOMER"),
        )
        ticket_count = self._customer_ticket_selector.get_by_customer_for_count(customer)
        customer_ticket_count_data = self.OutputSerializer(ticket_count).data
        return Response(data=customer_ticket_count_data, status=status.HTTP_200_OK)


class CustomerReservationListAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        is_active_customer = serializers.BooleanField(label="고객의 활성화 여부")
        reservation = inline_serializer(
            label="예약 목록",
            many=True,
            fields={
                "ticket_type": serializers.CharField(label="티켓 타입"),
                "start_at": serializers.DateTimeField(label="예약 시작 시간", format="%Y-%m-%d %H:%M"),
                "end_at": serializers.DateTimeField(label="예약 종료 시간", format="%Y-%m-%d %H:%M"),
                "customer_pet_name": serializers.CharField(label="반려동물 이름"),
            },
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._reservation_selector = ReservationContainer.reservation_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden = request.pet_kindergarden
        customer = get_object_or_not_found(
            self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden.id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )
        reservation = self._reservation_selector.get_queryset_by_customer_and_pet_kindergarden(
            customer, pet_kindergarden
        )
        data = self.OutputSerializer(
            {
                "is_active_customer": customer.is_active,
                "reservation": reservation,
            }
        ).data
        return Response(data=data, status=status.HTTP_200_OK)


class CustomerReservationDetailListAPI(APIAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(
            default=10,
            min_value=1,
            max_value=50,
            help_text="페이지당 조회 개수",
        )
        offset = serializers.IntegerField(default=0, min_value=0, help_text="페이지 오프셋")

    class OutputSerializer(BaseSerializer):
        reservation_id = serializers.IntegerField(label="예약 ID")
        ticket_type = serializers.CharField(label="티켓 타입")
        register_at = serializers.DateTimeField(label="등록 시간", format="%Y-%m-%d %H:%M")
        reserved_at = serializers.DateTimeField(label="예약 시간", format="%Y-%m-%d %H:%M")
        customer_pet_name = serializers.CharField(label="반려동물 이름")
        is_attended = serializers.BooleanField(label="참석 여부")
        is_cancellable = serializers.BooleanField(label="당일 취소 가능 여부")
        usage_time = serializers.IntegerField(label="사용 시간", required=False, allow_null=True)
        used_ticket_count = serializers.IntegerField(label="사용한 티켓 횟수", required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._reservation_selector = ReservationContainer.reservation_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden = request.pet_kindergarden
        customer = get_object_or_not_found(
            self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden.id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )
        reservation = self._reservation_selector.get_queryset_by_customer_and_pet_kindergarden_for_detail(
            customer, pet_kindergarden
        )
        pagination_reservation_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=reservation,
            request=request,
            view=self,
        )
        return Response(data=pagination_reservation_data, status=status.HTTP_200_OK)
