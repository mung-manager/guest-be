from datetime import datetime, timedelta
from typing import Any, Optional

from django.db.models import QuerySet

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.customers.models import Customer
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.pet_kindergardens.enums import ReservationAvailabilityOption
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.reservations.selectors.daily_reservations import (
    DailyReservationSelector,
)
from mung_manager.reservations.selectors.days_off import DayOffSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService


class ReservationService(AbstractReservationService):
    """
    이 클래스는 예약을 DB에 PUSH하는 비즈니스 로직을 담당합니다.
    """

    def __init__(
        self,
        customer_ticket_selector: CustomerTicketSelector,
        day_off_selector: DayOffSelector,
        pet_kindergarden_selector: PetKindergardenSelector,
        daily_reservation_selector: DailyReservationSelector,
    ):
        self._customer_ticket_selector = customer_ticket_selector
        self._day_off_selector = day_off_selector
        self._pet_kindergarden_selector = pet_kindergarden_selector
        self._daily_reservation_selector = daily_reservation_selector

    def extract_available_reservation_dates(
        self,
        tickets: QuerySet[Any],
        day_off_dates: list[Optional[str]],
        fully_booked_dates: list[Optional[str]],
        start_date: str,
    ) -> list[dict[str, Any]]:
        """
        휴무일 날짜 범위와 반려동물 유치원 아이디로 티켓별 예약 가능한 날짜 목록을 조회합니다.

        Args:
            tickets (QuerySet[Any]): 특정 타입의 티켓 쿼리셋
            day_off_dates (List[str]): 휴무일 리스트
            fully_booked_dates (List[str]): 정원을 초과한 날짜 리스트
            start_date (str): 시작 날짜

        Returns:
            list[dict[str, Any]]: 티켓 정보와 예약 가능한 날짜 목록
        """
        current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        available_dates_per_ticket = []
        for ticket in tickets:
            ticket_dates = []
            while current_date <= ticket.expired_at.date() and ticket.unused_count > 0:
                current_date_str = current_date.strftime("%Y-%m-%d")
                if current_date_str not in day_off_dates and current_date_str not in fully_booked_dates:
                    ticket_dates.append(current_date_str)
                current_date += timedelta(days=1)

            available_dates_per_ticket.append(
                {
                    "id": ticket.id,
                    "expired_at": ticket.expired_at.strftime("%Y-%m-%d"),
                    "unused_count": ticket.unused_count,
                    "dates": ticket_dates,
                }
            )

        return available_dates_per_ticket

    def calculate_available_reservation_dates(
        self, pet_kindergarden_id: int, customer: Customer, ticket_type: str
    ) -> list[dict[str, Any]]:
        """
        반려동물 유치원 아이디, 고객 객체, 티켓 타입으로 티켓별 예약 가능한 날짜 목록을 계산합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            customer (Customer): 고객 객체
            ticket_type (str): 티켓 타입

        Returns:
            list[dict[str, Any]]: 티켓 정보와 예약 가능한 날짜 목록
        """
        # 당일 예약 여부 조회
        reservation_availability_option = (
            self._pet_kindergarden_selector.get_by_pet_kindergarden_id_for_reservation_availability_option(
                pet_kindergarden_id=pet_kindergarden_id
            )
        )

        # 선택한 유형의 티켓 중 만료되지 않은 티켓의 목록
        tickets = check_object_or_not_found(
            self._customer_ticket_selector.get_queryset_by_customer_and_ticket_type(
                customer=customer, ticket_type=ticket_type
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
            code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
        )

        # 검색할 시작 날짜와 종료 날짜
        start_date = (
            datetime.now().strftime("%Y-%m-%d")
            if reservation_availability_option.first() == ReservationAvailabilityOption.SAME_DAY_AVAILABILITY.value
            else (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        end_date = tickets.first().expired_at.strftime("%Y-%m-%d")

        # 휴무일 목록 조회
        day_off_dates = self._day_off_selector.get_queryset_by_pet_kindergarden_id_and_date_range_for_day_off(
            pet_kindergarden_id=pet_kindergarden_id, date_range=[start_date, end_date]
        )

        # 해당 유치원의 최대 정원
        daily_pet_limit = self._pet_kindergarden_selector.get_by_pet_kindergarden_id_for_daily_pet_limit(
            pet_kindergarden_id=pet_kindergarden_id
        )

        # 정원이 초과된 날짜 목록 조회
        fully_booked_dates = self._daily_reservation_selector.get_queryset_for_fully_booked(
            pet_kindergarden_id=pet_kindergarden_id,
            date_range=[start_date, end_date],
            daily_pet_limit=daily_pet_limit,
        )

        # 예약 가능한 날짜 추출
        available_dates_per_ticket = self.extract_available_reservation_dates(
            tickets=tickets,
            day_off_dates=day_off_dates,
            fully_booked_dates=fully_booked_dates,
            start_date=start_date,
        )

        return available_dates_per_ticket
