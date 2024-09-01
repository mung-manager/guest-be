from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthMixin
from mung_manager.commons.base.serializers import BaseSerializer
from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import get_object_or_permission_denied, get_object_or_not_found
from mung_manager.commons.validators import (
    AvailableDatesAPIParameterValidator,
    InvalidTicketTypeValidator,
)
from mung_manager.customers.containers import CustomerContainer
from mung_manager.reservations.containers import ReservationContainer


class ReservationCustomerPetListAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(label="반려동물 아이디")
        name = serializers.CharField(label="반려동물 이름")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_pet_selector = CustomerContainer.customer_pet_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden = request.pet_kindergarden
        customer = get_object_or_not_found(
            self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden.id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )
        pets = self._customer_pet_selector.get_queryset_by_customer(customer)
        customer_pets_data = self.OutputSerializer(pets, many=True).data
        return Response(data=customer_pets_data, status=status.HTTP_200_OK)


class ReservationCustomerTicketTypesAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        ticket_types = serializers.ListField(label="티켓 타입 목록")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_ticket_selector = CustomerContainer.customer_ticket_selector()

    def get(self, request: Request) -> Response:
        user = request.user
        pet_kindergarden = request.pet_kindergarden
        customer = get_object_or_not_found(
            self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden.id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )
        ticket_types = self._customer_ticket_selector.get_queryset_by_customer(customer)
        ticket_types_data = self.OutputSerializer(ticket_types).data
        return Response(data=ticket_types_data, status=status.HTTP_200_OK)


class ReservationCustomerTicketTypeDetailAPI(APIAuthMixin, APIView):
    class InputSerializer(BaseSerializer):
        ticket_type = serializers.CharField(label="티켓 타입", validators=[InvalidTicketTypeValidator()])

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(label="고객 티켓 아이디")
        expired_at = serializers.DateTimeField(label="만료 시간")
        unused_count = serializers.IntegerField(label="잔여 횟수")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_ticket_selector = CustomerContainer.customer_ticket_selector()

    def get(self, request: Request) -> Response:
        input_serializer = self.InputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        user = request.user
        pet_kindergarden = request.pet_kindergarden
        customer = get_object_or_not_found(
            self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden.id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )
        tickets = self._customer_ticket_selector.get_queryset_by_customer_and_ticket_type_for_ticket_detail(
            customer, input_serializer.validated_data["ticket_type"]
        )
        customer_tickets_data = self.OutputSerializer(tickets, many=True).data
        return Response(data=customer_tickets_data, status=status.HTTP_200_OK)


class ReservationTicketCheckExpirationAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        customer_ticket_id = serializers.IntegerField(label="티켓 아이디", source="customer_ticket__id")
        expired_at = serializers.DateTimeField(
            label="만료 일자", format="%Y-%m-%d", source="customer_ticket__expired_at"
        )
        is_expired = serializers.BooleanField(label="만료 여부")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reservation_selector = ReservationContainer.reservation_selector()
        self._reservation_service = ReservationContainer.reservation_service()

    def get(self, request: Request, reservation_id: int) -> Response:
        reservation_ids = self._reservation_service.get_associated_reservation_ids_by_reservation_id(
            reservation_id=reservation_id
        )
        customer_tickets = self._reservation_selector.get_queryset_with_customer_ticket_by_ids(
            reservation_ids=reservation_ids
        )
        customer_tickets_data = self.OutputSerializer(customer_tickets, many=True).data
        return Response(data=customer_tickets_data, status=status.HTTP_200_OK)


class ReservationPetKindergardenAvailableDatesAPI(APIAuthMixin, APIView):
    class InputSerializer(BaseSerializer):
        ticket_type = serializers.CharField(label="티켓 타입", validators=[InvalidTicketTypeValidator()])
        ticket_id = serializers.IntegerField(label="티켓 아이디", required=False)

        class Meta:
            validators = [AvailableDatesAPIParameterValidator()]

    class OutputSerializer(BaseSerializer):
        available_dates = serializers.ListField(child=serializers.CharField(), label="예약 가능한 날짜 목록")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._reservation_service = ReservationContainer.reservation_service()

    def get(self, request: Request) -> Response:
        input_serializer = self.InputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        user = request.user
        pet_kindergarden = request.pet_kindergarden
        customer = get_object_or_not_found(
            self._customer_selector.get_by_user_and_pet_kindergarden_id(user, pet_kindergarden.id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )
        available_dates_data = self._reservation_service.get_available_reservation_dates(
            pet_kindergarden_id=pet_kindergarden.id,
            customer=customer,
            ticket_type=input_serializer.validated_data.get("ticket_type"),
            ticket_id=input_serializer.validated_data.get("ticket_id"),
        )
        available_dates_per_ticket_data = self.OutputSerializer({"available_dates": available_dates_data}).data
        return Response(data=available_dates_per_ticket_data, status=status.HTTP_200_OK)


class ReservationPetKindergardenAttendanceTimesAPI(APIAuthMixin, APIView):
    class InputSerializer(BaseSerializer):
        usage_time = serializers.IntegerField(label="사용 가능한 시간")

    class OutputSerializer(BaseSerializer):
        attendance_times = serializers.ListField(child=serializers.CharField(), label="등원 가능 시간")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reservation_service = ReservationContainer.reservation_service()

    def get(self, request: Request) -> Response:
        input_serializer = self.InputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        attendance_times = self._reservation_service.get_available_timeslots(
            business_start_hour=request.pet_kindergarden.business_start_hour,
            business_end_hour=request.pet_kindergarden.business_end_hour,
            usage_time=input_serializer.validated_data["usage_time"],
        )
        attendance_times_data = self.OutputSerializer({"attendance_times": attendance_times}).data
        return Response(data=attendance_times_data, status=status.HTTP_200_OK)
