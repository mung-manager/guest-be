from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthWithPetKindergardenAccessMixin
from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import get_object_or_not_found
from mung_manager.customers.containers import CustomerContainer
from mung_manager.customers.serializers import (
    CustomerPetSerializer,
    CustomerTicketSerializer,
)
from mung_manager.reservations.containers import ReservationContainer


class CustomerPetAndTicketListAPI(APIAuthWithPetKindergardenAccessMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        customer_pets = CustomerPetSerializer(many=True, label="고객 반려동물 목록")
        customer_tickets = CustomerTicketSerializer(many=True, label="고객 티켓 목록")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_pet_selector = CustomerContainer.customer_pet_selector()
        self._customer_ticket_selector = CustomerContainer.customer_ticket_selector()
        self._reservation_service = ReservationContainer.reservation_service()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden_id = request.pet_kindergarden_id
        customer = get_object_or_not_found(
            self._customer_selector.get_by_user_and_pet_kindergarden_id_for_active_customer(user, pet_kindergarden_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )

        pets = self._customer_pet_selector.get_queryset_by_customer(customer)
        tickets = self._customer_ticket_selector.get_queryset_by_customer(customer)

        customer_pets_data = CustomerPetSerializer(pets, many=True).data
        customer_tickets_data = CustomerTicketSerializer(tickets).data

        data = {
            "customer_pets": customer_pets_data,
            "customer_tickets": customer_tickets_data,
        }
        return Response(data=data, status=status.HTTP_200_OK)
