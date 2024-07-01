from datetime import datetime, timedelta

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
from mung_manager.pet_kindergardens.containers import PetKindergardenContainer
from mung_manager.pet_kindergardens.enums import ReservationAvailabilityOption
from mung_manager.reservations.containers import ReservationContainer
from mung_manager.tickets.enums import TicketType


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


class ReservationCalendarDateListAPI(APIAuthWithPetKindergardenAccessMixin, APIView):
    class InputSerializer(serializers.Serializer):
        ticket_type = serializers.ChoiceField(choices=[type.value for type in TicketType], label="티켓 타입")

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(label="고객 티켓 아이디")
        expired_at = serializers.DateTimeField(label="만료 시간")
        unused_count = serializers.IntegerField(label="잔여 횟수")
        dates = serializers.ListSerializer(child=serializers.CharField(), label="예약 가능한 날짜 목록")  # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()
        self._customer_ticket_selector = CustomerContainer.customer_ticket_selector()
        self._day_off_selector = ReservationContainer.day_off_selector()
        self._pet_kindergarden_selector = PetKindergardenContainer.pet_kindergarden_selector()
        self._daily_reservation_selector = ReservationContainer.daily_reservation_selector()
        self._reservation_service = ReservationContainer.reservation_service()

    def get(self, request: Request) -> Response:
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = request.user
        pet_kindergarden_id = request.pet_kindergarden_id
        customer = get_object_or_permission_denied(
            self._customer_selector.get_by_user_and_pet_kindergarden_id_for_active_customer(user, pet_kindergarden_id),
            msg=SYSTEM_CODE.message("INACTIVE_CUSTOMER"),
            code=SYSTEM_CODE.code("INACTIVE_CUSTOMER"),
        )
        ticket_type = input_serializer.validated_data.get("ticket_type")

        # 0. (시작값 추출)당일 예약 여부 조회
        reservation_availability_option = (
            self._pet_kindergarden_selector.get_by_pet_kindergarden_id_for_reservation_availability_option(
                pet_kindergarden_id=pet_kindergarden_id
            )
        )

        # 1. 선택한 유형의 티켓의 정보(만료되지 않은 티켓의 목록)
        tickets = self._customer_ticket_selector.get_queryset_by_customer_and_ticket_type(
            customer=customer, ticket_type=ticket_type
        )

        # 검색할 시작 날짜와 종료 날짜
        start_date = (
            datetime.now().strftime("%Y-%m-%d")
            if reservation_availability_option.first() == ReservationAvailabilityOption.SAME_DAY_AVAILABILITY.value
            else (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        end_date = tickets.first().expired_at.strftime("%Y-%m-%d")

        # 2. 휴무일
        day_off_dates = self._day_off_selector.get_queryset_by_pet_kindergarden_id_and_date_range_for_day_off(
            pet_kindergarden_id=pet_kindergarden_id, date_range=[start_date, end_date]
        )

        # 3. 정원 초과된 날짜 리스트 구하기
        # 해당 유치원의 정원 인원 가져욤
        daily_pet_limit = self._pet_kindergarden_selector.get_by_pet_kindergarden_id_for_daily_pet_limit(
            pet_kindergarden_id=pet_kindergarden_id
        )
        # 에약이 꽉찬 날짜 리스트
        fully_booked_dates = self._daily_reservation_selector.get_queryset_for_fully_booked(
            pet_kindergarden_id=pet_kindergarden_id,
            date_range=[start_date, end_date],
            daily_pet_limit=daily_pet_limit,
        )

        available_dates_per_ticket = self._reservation_service.extract_available_reservation_dates(
            tickets=tickets,
            day_off_dates=day_off_dates,
            fully_booked_dates=fully_booked_dates,
            start_date=start_date,
        )

        available_dates_per_ticket_data = self.OutputSerializer(available_dates_per_ticket, many=True).data
        return Response(data=available_dates_per_ticket_data, status=status.HTTP_200_OK)
