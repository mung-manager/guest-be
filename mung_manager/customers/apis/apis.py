from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthMixin
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


class ReservationListAPI(APIAuthMixin, APIView):
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
