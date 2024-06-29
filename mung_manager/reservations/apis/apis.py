from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthWithPetKindergardenAccessMixin
from mung_manager.customers.containers import CustomerContainer
from mung_manager.customers.serializers import (
    CustomerPetSerializer,
    CustomerTicketOutputSerializer,
)
from mung_manager.reservations.containers import ReservationContainer


class CustomerPetAndTicketListAPI(APIAuthWithPetKindergardenAccessMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        customer_pets = CustomerPetSerializer(many=True, label="고객 반려동물 목록")
        customer_tickets = serializers.DictField(
            child=serializers.ListSerializer(child=CustomerTicketOutputSerializer()), label="고객 티켓 목록"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_pet_selector = CustomerContainer.customer_pet_selector()
        self._reservation_service = ReservationContainer.reservation_service()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden_id = request.pet_kindergarden_id
        customer = self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden_id)

        pets = self._customer_pet_selector.get_queryset_by_customer_for_pet(customer)
        tickets = self._customer_selector.get_queryset_by_customer_for_ticket(customer)
        sorted_grouped_tickets = self._reservation_service.group_and_sort_tickets(tickets)

        output_serializer = self.OutputSerializer(
            data={
                "customer_pets": CustomerPetSerializer(pets, many=True).data,
                "customer_tickets": sorted_grouped_tickets,
            }
        )
        output_serializer.is_valid(raise_exception=True)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)
