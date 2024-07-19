from datetime import datetime

from concurrency.exceptions import RecordModifiedError
from django.db.models import F

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.customers.models import (
    Customer,
    CustomerTicket,
    CustomerTicketUsageLog,
)
from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerPetSelector,
    AbstractCustomerTicketSelector,
)
from mung_manager.errors.exceptions import ValidationException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.enums import ReservationStatus
from mung_manager.reservations.models import DailyReservation, Reservation
from mung_manager.reservations.selectors.abstracts import AbstractReservationSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import (
    AbstractReservationStrategy,
)


class AllDayReservationStrategy(AbstractReservationStrategy):

    def __init__(
        self,
        customer_pet_selector: AbstractCustomerPetSelector,
        reservation_service: AbstractReservationService,
        customer_ticket_selector: AbstractCustomerTicketSelector,
        reservation_selector: AbstractReservationSelector,
    ):
        super().__init__(customer_pet_selector, reservation_service)
        self._customer_ticket_selector = customer_ticket_selector
        self._reservation_selector = reservation_selector

    def specific_validation(
        self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict
    ) -> None:

        # 해당 고객이 주어진 티켓 타입과 티켓 아이디에 해당하는 티켓을 소유하고 있는지 검증
        check_object_or_not_found(
            self._customer_ticket_selector.get_for_all_day_or_time_ticket_type(
                customer=customer,
                ticket_type=reservation_data["ticket_type"],
                ticket_id=reservation_data["ticket_id"],
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
            code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
        )

        # 해당 날짜에 예약 여부 검증
        if reservation_data["reserved_date"].strftime(
            "%Y-%m-%d"
        ) in self._reservation_selector.get_queryset_for_duplicate_reservation(
            customer_id=customer.id,
            customer_pet_id=reservation_data["pet_id"],
            customer_ticket_id=reservation_data["ticket_id"],
            pet_kindergarden_id=pet_kindergarden.id,
        ):
            raise ValidationException(
                detail=SYSTEM_CODE.message("ALREADY_EXISTS_RESERVATION"),
                code=SYSTEM_CODE.code("ALREADY_EXISTS_RESERVATION"),
            )

    def get_customer_tickets(self, customer: Customer, reservation_data: dict) -> CustomerTicket:
        """
        이 함수는 주어진 정보를 바탕으로 티켓(들)을 반환합니다.
        티켓 횟수 증감 처리를 낙관적 락을 통해 구현했습니다.
        유저의 혼란을 방지하고자 재시도 로직은 구현하지 않았습니다.

        Args:
            customer (Customer): 영업 시작 시간
            reservation_data (dict): 사용자 입력

        Returns:
            CustomerTicket: 고객 티켓 객체
        """

        customer_ticket = self._customer_ticket_selector.get_with_ticket_by_id_and_customer_id(
            customer_ticket_id=reservation_data["ticket_id"],
            customer_id=customer.id,
        )
        if customer_ticket is None:
            raise ValidationException(
                detail=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_TICKET"),
                code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_TICKET"),
            )

        try:
            customer_ticket.used_count += 1
            customer_ticket.unused_count -= 1
            customer_ticket.save(update_fields=["used_count", "unused_count", "updated_at", "version"])
        except RecordModifiedError:
            raise ValidationException(
                detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
            )

        return customer_ticket

    def create_reservations(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict,
    ) -> Reservation:
        """
        이 함수는 주어진 정보를 활용하여 예약을 생성합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict): 사용자 입력

        Returns:
            Reservation: 예약 객체
        """

        reserved_at = datetime.combine(reservation_data["reserved_date"].date(), pet_kindergarden.business_start_hour)
        end_at = datetime.combine(reservation_data["reserved_date"].date(), pet_kindergarden.business_end_hour)
        reservation = Reservation.objects.create(
            reserved_at=reserved_at,
            end_at=end_at,
            is_attended=False,
            reservation_status=ReservationStatus.COMPLETED.value,
            pet_kindergarden_id=pet_kindergarden.id,
            customer_id=customer.id,
            customer_pet_id=reservation_data["pet_id"],
            customer_ticket_id=reservation_data["ticket_id"],
        )

        return reservation

    def handle_daily_reservations(self, pet_kindergarden: PetKindergarden, reservation_data: dict) -> None:
        """
        이 함수는 일간 예약과 관련된 정보를 처리합니다.

        Args:
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict): 사용자 입력

        Returns:
            None
        """

        reserved_at = datetime.combine(reservation_data["reserved_date"].date(), pet_kindergarden.business_start_hour)
        daily_reservation, created = DailyReservation.objects.get_or_create(
            pet_kindergarden_id=pet_kindergarden.id,
            reserved_at=reserved_at,
            defaults={"total_pet_count": 1, "all_day_pet_count": 1},
        )
        if not created:
            DailyReservation.objects.filter(pet_kindergarden_id=pet_kindergarden.id, reserved_at=reserved_at).update(
                time_pet_count=F("all_day_pet_count") + 1, total_pet_count=F("total_pet_count") + 1
            )

    def handle_tickets_usage(self, customer_ticket: CustomerTicket, reservation: Reservation) -> None:
        """
        이 함수는 고객 티켓 사용 로그를 생성합니다.

        Args:
            customer_ticket (CustomerTicket): 고객 티켓 객체
            reservation (Reservation): 예약 객체

        Returns:
            None
        """

        CustomerTicketUsageLog.objects.create(
            customer_ticket_id=customer_ticket.id,
            reservation_id=reservation.id,
            used_count=1,
        )
