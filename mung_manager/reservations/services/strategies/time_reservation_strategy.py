from datetime import datetime, timedelta
from typing import Any, Optional

from concurrency.exceptions import RecordModifiedError
from django.db.models import F


from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerPetSelector,
    AbstractCustomerTicketSelector,
)
from mung_manager.errors.exceptions import ValidationException
from mung_manager_commons.constants import SYSTEM_CODE
from mung_manager_commons.selector import check_object_or_not_found
from mung_manager_db.enum_types import ReservationStatus
from mung_manager.reservations.selectors.abstracts import AbstractReservationSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import (
    AbstractReservationStrategy,
)
from mung_manager_db.models import Customer, CustomerTicket, CustomerTicketUsageLog, PetKindergarden, Reservation, \
    DailyReservation


class TimeReservationStrategy(AbstractReservationStrategy):

    def __init__(
        self,
        customer_pet_selector: AbstractCustomerPetSelector,
        reservation_service: AbstractReservationService,
        customer_ticket_selector: AbstractCustomerTicketSelector,
        reservation_selector: AbstractReservationSelector,
    ):
        super().__init__(customer_pet_selector, reservation_service, reservation_selector)
        self._customer_pet_selector = customer_pet_selector
        self._customer_ticket_selector = customer_ticket_selector
        self._reservation_selector = reservation_selector

    def specific_validation(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
    ) -> None:
        """
        이 함수는 시간권 예약에 대한 검증 로직을 실행합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력

        Returns:
            None
        """
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

        # 등원 시간 검증
        if reservation_data["attendance_time"].strftime(
            "%H:%M"
        ) not in self._reservation_service.get_available_timeslots(
            business_start_hour=pet_kindergarden.business_start_hour,
            business_end_hour=pet_kindergarden.business_end_hour,
            usage_time=int(reservation_data["ticket_type"][:-2]),
        ):
            raise ValidationException(
                detail=SYSTEM_CODE.message("INVALID_ATTENDANCE_TIME"),
                code=SYSTEM_CODE.code("INVALID_ATTENDANCE_TIME"),
            )

    def get_customer_tickets(
        self,
        customer: Customer,
        reservation_data: dict[str, Any],
    ) -> CustomerTicket:
        """
        이 함수는 주어진 정보를 바탕으로 티켓(들)을 반환합니다.
        티켓 횟수 증감 처리를 낙관적 락을 통해 구현했습니다.
        유저의 혼란을 방지하고자 재시도 로직은 구현하지 않았습니다.

        Args:
            customer (Customer): 영업 시작 시간
            reservation_data (dict[str, Any]): 사용자 입력

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

    def handle_daily_reservations(
        self,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
        customer: Customer,
    ) -> None:
        """
        이 함수는 일간 예약과 관련된 정보를 처리합니다.

        Args:
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력
            customer (Customer): 고객 객체

        Returns:
            None
        """
        reserved_at = datetime.combine(reservation_data["reserved_date"].date(), reservation_data["attendance_time"])
        daily_reservation, created = DailyReservation.objects.get_or_create(
            pet_kindergarden_id=pet_kindergarden.id,
            reserved_at=reserved_at,
            defaults={"total_pet_count": 1, "time_pet_count": 1},
        )
        if not created:
            DailyReservation.objects.filter(pet_kindergarden_id=pet_kindergarden.id, reserved_at=reserved_at).update(
                time_pet_count=F("time_pet_count") + 1, total_pet_count=F("total_pet_count") + 1
            )

    def create_reservations(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
        customer_tickets: Optional[list[CustomerTicket]] = None,
    ) -> Reservation:
        """
        이 함수는 주어진 정보를 활용하여 예약을 생성합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력
            customer_tickets (Optional[list[CustomerTicket]]): 예약에 사용된 티켓 정보

        Returns:
            Reservation: 예약 객체
        """
        reserved_at = datetime.combine(reservation_data["reserved_date"].date(), reservation_data["attendance_time"])
        end_at = reserved_at + timedelta(hours=int(reservation_data["ticket_type"][:-2]))
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

    def handle_tickets_usage(
        self,
        customer_tickets: CustomerTicket,
        reservations: Reservation,
    ) -> None:
        """
        이 함수는 고객 티켓 사용 로그를 생성합니다.

        Args:
            customer_tickets (CustomerTicket): 고객 티켓 객체
            reservations (Reservation): 예약 객체

        Returns:
            None
        """
        CustomerTicketUsageLog.objects.create(
            customer_ticket_id=customer_tickets.id,
            reservation_id=reservations.id,
            used_count=1,
        )

    def get_reservation_info(
        self,
        reservation_data: dict[str, Any],
        customer_tickets: CustomerTicket,
    ) -> dict[str, Any]:
        """
        이 함수는 생성한 예약 정보를 반환합니다.

        Args:
            reservation_data (dict[str, Any]): 사용자 입력
            customer_tickets (CustomerTicket): 고객 티켓 객체

        Returns:
            dict[str, Any]`: 예약 정보 반환
        """
        unused_count = self._customer_ticket_selector.get_by_customer_ticket_id_for_unused_count(customer_tickets.id)
        pet_name = self._customer_pet_selector.get_by_pet_id_for_pet_name(reservation_data["pet_id"])
        duration = int(reservation_data["ticket_type"][:-2])

        reserved_date = reservation_data["reserved_date"]
        attendance_time = reservation_data["attendance_time"]
        attendance_datetime = datetime.combine(reserved_date.date(), attendance_time)
        check_out_time_datetime = attendance_datetime + timedelta(hours=duration)
        check_out_time = check_out_time_datetime.time()
        reservation_info = {
            "attendance_date": reservation_data["reserved_date"],
            "check_in_time": reservation_data["attendance_time"],
            "check_out_time": check_out_time,
            "usage_count": 1,
            "remain_count": unused_count,
            "pet_name": pet_name,
        }

        return reservation_info
