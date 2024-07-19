from datetime import datetime, timedelta

from concurrency.exceptions import RecordModifiedError
from django.db.models import F

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.customers.models import Customer, CustomerTicketUsageLog
from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerPetSelector,
    AbstractCustomerTicketSelector,
)
from mung_manager.errors.exceptions import ValidationException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.enums import ReservationStatus
from mung_manager.reservations.models import DailyReservation, Reservation
from mung_manager.reservations.selectors.abstracts import (
    AbstractDailyReservationSelector,
    AbstractReservationSelector,
)
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import (
    AbstractReservationStrategy,
)


class TimeReservationStrategy(AbstractReservationStrategy):

    def __init__(
        self,
        customer_pet_selector: AbstractCustomerPetSelector,
        reservation_service: AbstractReservationService,
        customer_ticket_selector: AbstractCustomerTicketSelector,
        daily_reservation_selector: AbstractDailyReservationSelector,
        reservation_selector: AbstractReservationSelector,
    ):
        super().__init__(customer_pet_selector, reservation_service)
        self._customer_ticket_selector = customer_ticket_selector
        self._daily_reservation_selector = daily_reservation_selector
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

    def reserve(self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict) -> None:

        # 티켓 횟수 증감 처리(낙관적 락 구현)
        # 재시도 로직 필요 x -> 유저 혼란 방지
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
            customer_ticket.save(update_fields=["used_count", "unused_count", "version"])
        except RecordModifiedError:
            raise ValidationException(
                detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
            )

        # 예약 생성
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

        # 일간 예약 생성 및 증가 처리
        daily_reservation, created = DailyReservation.objects.get_or_create(
            pet_kindergarden_id=pet_kindergarden.id,
            reserved_at=reserved_at,
            defaults={"total_pet_count": 1, "time_pet_count": 1},
        )
        if not created:
            DailyReservation.objects.filter(pet_kindergarden_id=pet_kindergarden.id, reserved_at=reserved_at).update(
                time_pet_count=F("time_pet_count") + 1, total_pet_count=F("total_pet_count") + 1
            )

        # 고객 티켓 사용 로그 생성
        CustomerTicketUsageLog.objects.create(
            customer_ticket_id=customer_ticket.id,
            reservation_id=reservation.id,
            used_count=1,
        )
