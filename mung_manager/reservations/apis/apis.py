from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthWithPetKindergardenAccessMixin
from mung_manager.customers.containers import CustomerContainer
from mung_manager.customers.serializers import CustomerPetSerializer, CustomerTicketSerializer


class CustomerPetAndTicketListAPI(APIAuthWithPetKindergardenAccessMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        customer_pets = CustomerPetSerializer(many=True, label="반려동물 목록")
        customer_tickets = CustomerTicketSerializer(many=True, label="티켓 목록")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden_id = request.pet_kindergarden_id
        customer = self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden_id)

        pets = self._customer_selector.get_queryset_by_customer_for_pet(customer)
        tickets = self._customer_selector.get_queryset_by_customer_for_ticket(customer)

        data = {
            "customer_pets": CustomerPetSerializer(pets, many=True).data,
            "customer_tickets": CustomerTicketSerializer(tickets, many=True).data,
        }
        output_serializer = self.OutputSerializer(data=data)
        output_serializer.is_valid(raise_exception=True)
        return Response(data=output_serializer.data, status=status.HTTP_200_OK)