from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthWithPetKindergardenAccessMixin
from mung_manager.commons.base.serializers import BaseSerializer
from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import get_object_or_permission_denied
from mung_manager.commons.utils import inline_serializer
from mung_manager.customers.containers import CustomerContainer


class ReservationCustomerPetListAPI(APIAuthWithPetKindergardenAccessMixin, APIView):
    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(label="반려동물 아이디")
        name = serializers.CharField(label="반려동물 이름")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_pet_selector = CustomerContainer.customer_pet_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden_id = request.pet_kindergarden_id
        customer = get_object_or_permission_denied(
            self._customer_selector.get_by_user_and_pet_kindergarden_id_for_active_customer(user, pet_kindergarden_id),
            msg=SYSTEM_CODE.message("INACTIVE_CUSTOMER"),
            code=SYSTEM_CODE.code("INACTIVE_CUSTOMER"),
        )
        pets = self._customer_pet_selector.get_queryset_by_customer(customer)
        customer_pets_data = self.OutputSerializer(pets, many=True).data
        return Response(data=customer_pets_data, status=status.HTTP_200_OK)


class ReservationCustomerTicketListAPI(APIAuthWithPetKindergardenAccessMixin, APIView):
    class OutputSerializer(BaseSerializer):
        time = inline_serializer(
            label="시간권 예약",
            many=True,
            fields={
                "id": serializers.IntegerField(label="고객 티켓 아이디"),
                "expired_at": serializers.DateTimeField(label="만료 시간"),
                "unused_count": serializers.IntegerField(label="잔여 횟수"),
                "usage_time": serializers.IntegerField(label="사용 가능한 시간", source="ticket.usage_time"),
            },
        )
        all_day = inline_serializer(
            label="종일권 예약",
            many=True,
            fields={
                "id": serializers.IntegerField(label="고객 티켓 아이디"),
                "expired_at": serializers.DateTimeField(label="만료 시간"),
                "unused_count": serializers.IntegerField(label="잔여 횟수"),
            },
        )
        hotel = inline_serializer(
            label="호텔권 예약",
            many=True,
            fields={
                "id": serializers.IntegerField(label="고객 티켓 아이디"),
                "expired_at": serializers.DateTimeField(label="만료 시간"),
                "unused_count": serializers.IntegerField(label="잔여 횟수"),
            },
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_ticket_selector = CustomerContainer.customer_ticket_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden_id = request.pet_kindergarden_id
        customer = get_object_or_permission_denied(
            self._customer_selector.get_by_user_and_pet_kindergarden_id_for_active_customer(user, pet_kindergarden_id),
            msg=SYSTEM_CODE.message("INACTIVE_CUSTOMER"),
            code=SYSTEM_CODE.code("INACTIVE_CUSTOMER"),
        )
        tickets = self._customer_ticket_selector.get_queryset_by_customer(customer)
        customer_tickets_data = self.OutputSerializer(tickets).data
        return Response(data=customer_tickets_data, status=status.HTTP_200_OK)
