from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthMixin
from mung_manager.commons.base.serializers import BaseSerializer
from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import get_object_or_permission_denied
from mung_manager.customers.containers import CustomerContainer


class CustomerTicketCountAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        time = serializers.IntegerField(label="시간권 예약")
        all_day = serializers.IntegerField(label="종일권 예약")
        hotel = serializers.IntegerField(label="호텔권 예약")

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
