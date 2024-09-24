from datetime import date, datetime, time, timedelta
from typing import Optional

from concurrency.exceptions import RecordModifiedError
from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone
from django_stubs_ext import ValuesQuerySet


from mung_manager.customers.selectors.customer_pets import CustomerPetSelector
from mung_manager.customers.selectors.customer_ticket_usage_logs import (
    CustomerTicketUsageLogSelector,
)
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.errors.exceptions import ValidationException

from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager_commons.constants import SYSTEM_CODE
from mung_manager_commons.selector import get_object_or_not_found
from mung_manager_db.enum_types import ReservationStatus, TicketType
from mung_manager.reservations.selectors.daily_reservations import (
    DailyReservationSelector,
)
from mung_manager.reservations.selectors.days_off import DayOffSelector
from mung_manager.reservations.selectors.reservations import ReservationSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import (
    AbstractReservationStrategy,
)
from mung_manager.reservations.services.strategies.strategy_factory import (
    ReservationStrategyFactory,
)

from mung_manager_db.enum_types import ReservationChangeOption, ReservationAvailabilityOption
from mung_manager_db.models import Customer, PetKindergarden, Reservation, DayOff, DailyReservation


class ReservationService(AbstractReservationService):
    """
    이 클래스는 예약과 관련된 비즈니스 로직을 담당합니다.
    """

    def __init__(
        self,
        reservation_selector: ReservationSelector,
        customer_ticket_usage_log_selector: CustomerTicketUsageLogSelector,
        daily_reservation_selector: DailyReservationSelector,
        customer_ticket_selector: CustomerTicketSelector,
        day_off_selector: DayOffSelector,
        pet_kindergarden_selector: PetKindergardenSelector,
        customer_pet_selector: CustomerPetSelector,
        strategy_factory: ReservationStrategyFactory,
    ):
        self._reservation_selector = reservation_selector
        self._daily_reservation_selector = daily_reservation_selector
        self._customer_ticket_usage_log_selector = customer_ticket_usage_log_selector
        self._customer_ticket_selector = customer_ticket_selector
        self._day_off_selector = day_off_selector
        self._pet_kindergarden_selector = pet_kindergarden_selector
        self._customer_pet_selector = customer_pet_selector
        self._strategy_factory = strategy_factory

    @staticmethod
    def validate_reservation_cancellation(pet_kindergarden: PetKindergarden, reservation: Reservation) -> None:
        """
        이 함수는 당일 취소 불가능 옵션이면서 취소하려는 예약 날짜가 오늘일 때를 검증합니다.

        Args:
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation (Reservation): 예약 객체

        Returns:
            None
        """
        if pet_kindergarden.reservation_change_option == ReservationChangeOption.SAME_DAY_UNCHANGE.value:
            if reservation.reserved_at.date() == timezone.now().date():
                raise ValidationException(
                    detail=SYSTEM_CODE.message("CANNOT_CANCEL_RESERVATION"),
                    code=SYSTEM_CODE.code("CANNOT_CANCEL_RESERVATION"),
                )

    @transaction.atomic
    def cancel_reservation(self, pet_kindergarden: PetKindergarden, reservation_id: int) -> None:
        """
        이 함수는 예약 아이디에 대한 검증을 하고 reservation 객체에 해당하는 예약을 취소합니다. 또한 필요 시 티켓의 횟수를 복구합니다.

        Args:
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_id (int): 예약 아이디

        Returns:
            None
        """
        reservation = get_object_or_not_found(
            self._reservation_selector.get_by_id_for_uncanceled_reservation(reservation_id=reservation_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_RESERVATION"),
            code=SYSTEM_CODE.code("NOT_FOUND_RESERVATION"),
        )
        self.validate_reservation_cancellation(pet_kindergarden, reservation)

        reservations = self.update_reservation_status_to_canceled(reservation)
        self.update_ticket_usage_logs(reservations)
        self.update_daily_reservations(reservations)
        self.restore_ticket_counts(reservations)

    def update_reservation_status_to_canceled(self, reservation: Reservation) -> QuerySet[Reservation]:
        """
        이 함수는 reservation 객체를 사용하여 단일 예약 또는 묶여있는 예약의 상태를 "취소"로 변경합니다.

        Args:
            reservation (Reservation): 예약 객체

        Returns:
            QuerySet[Reservation]: 예약 쿼리셋 반환
        """
        reservation_ids = [reservation.id]
        if reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value and reservation.is_extented:
            root_id = reservation.id
            child_ids = self._reservation_selector.get_child_ids_by_parent_id(parent_id=root_id)
            reservation_ids.extend(map(lambda x: x[0], child_ids))
        reservations = self._reservation_selector.get_queryset_with_customer_ticket_and_ticket_by_ids(
            reservation_ids=reservation_ids
        )
        reservations.update(reservation_status=ReservationStatus.CANCELED.value)
        return reservations

    def update_ticket_usage_logs(self, reservations: QuerySet[Reservation]) -> None:
        """
        이 함수는 전달 받은 예약 쿼리셋에 속하는 예약들의 사용 로그를 수정합니다.

        Args:
            reservations (QuerySet[Reservation]): 예약 쿼리셋

        Returns:
            None
        """
        reservation_ids = list(reservations.values_list("id", flat=True))
        customer_ticket_usage_logs = self._customer_ticket_usage_log_selector.get_queryset_by_reservation_ids(
            reservation_ids=reservation_ids,
        )
        customer_ticket_usage_logs.update(used_count=0)

    def update_daily_reservations(self, reservations: QuerySet[Reservation]) -> None:
        """
        이 함수는 전달 받은 예약 쿼리셋을 통해 일별 예약 현황을 수정합니다.

        Args:
            reservations (QuerySet[Reservation]): 예약 쿼리셋

        Returns:
            None
        """
        reservation = reservations[0]
        reserved_at = min(res.reserved_at for res in reservations)
        end_at = max(res.end_at for res in reservations if res.end_at is not None)
        daily_reservations = self._daily_reservation_selector.get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
            pet_kindergarden_id=reservation.pet_kindergarden_id,
            reserved_at=reserved_at,
            end_at=end_at,
        )
        if reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value:
            daily_reservations.update(
                total_pet_count=F("total_pet_count") - 1, hotel_pet_count=F("hotel_pet_count") - 1
            )
        if reservation.customer_ticket.ticket.ticket_type == TicketType.TIME.value:
            daily_reservations.update(total_pet_count=F("total_pet_count") - 1, time_pet_count=F("time_pet_count") - 1)
        if reservation.customer_ticket.ticket.ticket_type == TicketType.ALL_DAY.value:
            daily_reservations.update(
                total_pet_count=F("total_pet_count") - 1, all_day_pet_count=F("all_day_pet_count") - 1
            )

    def restore_ticket_counts(self, reservations: QuerySet[Reservation]) -> None:
        """
        이 함수는 만료 기간이 남은 이용권의 횟수를 복원합니다.

        Args:
            reservations (QuerySet[Reservation]): 예약 쿼리셋

        Returns:
            None
        """
        for reservation in reservations:
            if reservation.customer_ticket.expired_at.date() >= timezone.now().date():
                try:
                    customer_ticket = reservation.customer_ticket
                    customer_ticket.used_count -= 1
                    customer_ticket.unused_count += 1
                    customer_ticket.save(update_fields=["used_count", "unused_count", "version"])
                except RecordModifiedError:
                    raise ValidationException(
                        detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                        code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
                    )

    def get_associated_reservation_ids_by_reservation_id(self, reservation_id: int) -> list[int]:
        """
        이 함수는 예약 아이디를 통해 해당 예약을 이루고 있는 예약 아이디를 반환합니다.

        Args:
            reservation_id (int): 예약 아이디

        Returns:
            list[int]: 예약 아이디 리스트 반환
        """
        get_object_or_not_found(
            self._reservation_selector.get_by_id_for_uncanceled_reservation(reservation_id=reservation_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_RESERVATION"),
            code=SYSTEM_CODE.code("NOT_FOUND_RESERVATION"),
        )

        reservation_ids = [reservation_id]
        child_ids = self._reservation_selector.get_child_ids_by_parent_id(parent_id=reservation_id)
        reservation_ids.extend(map(lambda x: x[0], child_ids))
        return reservation_ids

    def filter_available_reservation_dates(
        self,
        start_date: datetime,
        end_date: datetime,
        day_off_dates_queryset: ValuesQuerySet[DayOff, date],
        fully_booked_dates_queryset: ValuesQuerySet[DailyReservation, date] | None,
    ) -> list[str]:
        """
        휴무일 날짜 범위와 반려동물 유치원 아이디로 티켓별 예약 가능한 날짜 목록을 조회합니다.

        Args:
            start_date (str): 시작 날짜
            end_date (str): 종료 날짜
            day_off_dates_queryset (ValuesQuerySet[DayOff, date]): 휴무일 쿼리셋
            fully_booked_dates_queryset (ValuesQuerySet[DailyReservation, date] | None): 정원을 초과한 날짜 쿼리셋

        Returns:
            list[str]: 티켓 정보와 예약 가능한 날짜 목록
        """
        day_off_dates = [day_off.strftime("%Y-%m-%d") for day_off in day_off_dates_queryset]
        fully_booked_dates = (
            [fully_booked.strftime("%Y-%m-%d") for fully_booked in fully_booked_dates_queryset]
            if fully_booked_dates_queryset
            else []
        )

        available_dates = []

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str not in day_off_dates and date_str not in fully_booked_dates:
                available_dates.append(date_str)
            current_date += timedelta(days=1)

        return available_dates

    def get_available_reservation_dates(
        self, pet_kindergarden_id: int, customer: Customer, ticket_type: str, ticket_id: Optional[int]
    ) -> list[str]:
        """
        반려동물 유치원 아이디, 고객 객체, 티켓 타입으로  예약 가능한 날짜 목록을 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            customer (Customer): 고객 객체
            ticket_type (str): 티켓 타입
            ticket_id (int): 티켓 아이디

        Returns:
            list[str]: 예약 가능한 날짜 리스트
        """
        # 당일 예약 여부 조회
        reservation_availability_option_queryset = (
            self._pet_kindergarden_selector.get_by_pet_kindergarden_id_for_reservation_availability_option(
                pet_kindergarden_id=pet_kindergarden_id
            )
        )

        # 티켓 조회(호텔권 -> 목록 조회, 시간/종일권 -> 단일 조회)
        if ticket_type == TicketType.HOTEL.value:
            tickets_queryset = get_object_or_not_found(
                self._customer_ticket_selector.get_queryset_by_customer_for_hotel_ticket_type(customer=customer),
                msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
                code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
            )
        else:
            tickets_queryset = get_object_or_not_found(
                self._customer_ticket_selector.get_for_all_day_or_time_ticket_type(
                    customer=customer,
                    ticket_type=ticket_type,
                    ticket_id=ticket_id,
                ),
                msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
                code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
            )

        # 검색할 시작 날짜와 종료 날짜
        start_date = (
            datetime.now()
            if reservation_availability_option_queryset.first()
            == ReservationAvailabilityOption.SAME_DAY_AVAILABILITY.value
            else (datetime.now() + timedelta(days=1))
        )
        end_date = (
            tickets_queryset.order_by("-expired_at").first().expired_at + timedelta(days=1)
            if ticket_type == TicketType.HOTEL.value
            else tickets_queryset.expired_at
        )

        # 휴무일 목록 조회
        day_off_dates_queryset = self._day_off_selector.get_queryset_by_pet_kindergarden_id_and_date_range_for_day_off(
            pet_kindergarden_id=pet_kindergarden_id, date_range=[start_date, end_date]
        )

        # 해당 유치원의 최대 정원
        daily_pet_limit = self._pet_kindergarden_selector.get_by_pet_kindergarden_id_for_daily_pet_limit(
            pet_kindergarden_id=pet_kindergarden_id
        )

        # 정원이 초과된 날짜 목록 조회
        fully_booked_dates_queryset = self._daily_reservation_selector.get_queryset_for_fully_booked(
            pet_kindergarden_id=pet_kindergarden_id,
            date_range=[start_date, end_date],
            daily_pet_limit=daily_pet_limit,
        )

        # 예약 가능한 날짜 추출
        available_dates = self.filter_available_reservation_dates(
            start_date=start_date,
            end_date=end_date,
            day_off_dates_queryset=day_off_dates_queryset,
            fully_booked_dates_queryset=fully_booked_dates_queryset,
        )

        return available_dates

    def get_available_timeslots(self, business_start_hour: time, business_end_hour: time, usage_time: int) -> list[str]:
        """
        이 함수는 운영 시간과 사용 가능한 시간을 통해 선택 가능한 등원 시간을 반환합니다.

        Args:
            business_start_hour (time): 영업 시작 시간
            business_end_hour (time): 영업 종료 시간
            usage_time (int): 사용 가능한 시간

        Returns:
            list[str]: 선택 가능한 등원 시간 리스트
        """
        today = date.today()
        start_datetime = datetime.combine(today, business_start_hour)
        end_datetime = datetime.combine(today, business_end_hour) - timedelta(hours=usage_time)

        available_times = []
        current_time = start_datetime
        while current_time <= end_datetime:
            available_times.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)

        return available_times

    def get_strategy(self, ticket_type: str) -> AbstractReservationStrategy:
        return self._strategy_factory.create_strategy(ticket_type, self)

    @transaction.atomic
    def register_reservation(
        self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict
    ) -> dict:
        """
        이 함수는 티켓의 유형에 맞게 값을 검증 후 예약을 생성합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 유치원 객체
            reservation_data (dict): 예약 관련 데이터로, 필드에는 다음의 값들이 포함됩니다:
                pet_id (int): 반려동물 아이디
                ticket_type (str): 티켓 타입 (예: "4시간", "종일", "호텔")
                ticket_id (int, optional): 티켓 아이디로, 호텔권일 경우 불필요
                reserved_date (datetime): 등원 날짜
                end_date (datetime, optional): 하원 날짜, 호텔권일 경우만 필요
                attendance_time (datetime, optional): 등원 시간으로, 시간권일 경우만 필요

        Returns:
            dict
        """
        ticket_type = reservation_data["ticket_type"][-2:]
        strategy = self.get_strategy(ticket_type)
        strategy.validate(customer, pet_kindergarden, reservation_data)
        reservation_info = strategy.reserve(customer, pet_kindergarden, reservation_data)

        return reservation_info
