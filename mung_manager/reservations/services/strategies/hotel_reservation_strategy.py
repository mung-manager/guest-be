from collections import defaultdict
from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter
from typing import Any, Optional

from concurrency.exceptions import RecordModifiedError
from django.db.models import F

from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerPetSelector,
    AbstractCustomerTicketSelector,
)
from mung_manager.reservations.selectors.abstracts import AbstractReservationSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import (
    AbstractReservationStrategy,
)
from mung_manager_commons.constants import SYSTEM_CODE
from mung_manager_commons.errors import (
    InvalidParameterFormatException,
    ValidationException,
)
from mung_manager_commons.selector import check_object_or_not_found
from mung_manager_db.enum_types import ReservationStatus, TicketType
from mung_manager_db.models import (
    Customer,
    CustomerTicket,
    CustomerTicketUsageLog,
    DailyReservation,
    PetKindergarden,
    Reservation,
)


class HotelReservationStrategy(AbstractReservationStrategy):

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
        self.reservation_dates: list[datetime] = []

    def specific_validation(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
    ) -> None:
        """
        이 함수는 호텔권 예약에 대한 검증 로직을 실행합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력

        Returns:
            None
        """
        # 사용 가능한 호텔 타입의 티켓이 존재하는지 검증
        check_object_or_not_found(
            self._customer_ticket_selector.get_queryset_by_customer_for_hotel_ticket_type(customer=customer),
            msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
            code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
        )

        # 등원 날짜가 하원 날짜보다 앞서있는지 검증
        if not reservation_data["reserved_date"] < reservation_data["end_date"]:
            raise ValidationException(
                detail=SYSTEM_CODE.message("INVALID_END_AT"),
                code=SYSTEM_CODE.code("INVALID_END_AT"),
            )

        # 등원 날짜와 하원 날짜 사이에 포함된 날짜들이 예약할 수 있는 날짜인지 검증
        available_dates = self._reservation_service.get_available_reservation_dates(
            pet_kindergarden_id=pet_kindergarden.id,
            customer=customer,
            ticket_type=reservation_data["ticket_type"],
            ticket_id=reservation_data.get("ticket_id"),
        )
        reserved_dates = self._reservation_selector.get_queryset_for_duplicate_reservation(
            customer_id=customer.id,
            customer_pet_id=reservation_data["pet_id"],
            pet_kindergarden_id=pet_kindergarden.id,
        )
        current_date = reservation_data["reserved_date"]
        while current_date <= reservation_data["end_date"]:
            # 휴일이거나 정원이 초과된 날인지 검증
            current_date_str = current_date.strftime("%Y-%m-%d")
            if current_date_str not in available_dates:
                raise ValidationException(
                    detail=SYSTEM_CODE.message("CANNOT_MAKE_RESERVATION"),
                    code=SYSTEM_CODE.code("CANNOT_MAKE_RESERVATION"),
                )

            # 해당 날에 이미 예약을 했는지 검증
            if current_date_str in reserved_dates:
                raise ValidationException(
                    detail=SYSTEM_CODE.message("ALREADY_EXISTS_RESERVATION"),
                    code=SYSTEM_CODE.code("ALREADY_EXISTS_RESERVATION"),
                )
            current_date += timedelta(days=1)

    def get_customer_tickets(
        self,
        customer: Customer,
        reservation_data: dict[str, Any],
    ) -> dict[CustomerTicket, list[datetime]]:
        """
        이 함수는 주어진 정보를 바탕으로 호텔 티켓 사용 현황을 반환합니다.
        티켓 횟수 증감 처리를 낙관적 락을 통해 구현했습니다.

        Args:
            customer (Customer): 고객 객체
            reservation_data (dict[str, Any]): 예약 정보

        Returns:
            dict[CustomerTicket, list[datetime]]: 티켓별 사용 날짜 목록
        """
        current_date = reservation_data["reserved_date"]
        while current_date < reservation_data["end_date"]:
            self.reservation_dates.append(current_date)
            current_date += timedelta(days=1)

        customer_tickets = defaultdict(list)
        for date in self.reservation_dates:
            available_tickets = (
                self._customer_ticket_selector.get_queryset_by_customer_and_ticket_type_for_ticket_detail(
                    customer, TicketType.HOTEL.value
                )
            )

            if not available_tickets.exists():
                raise ValidationException(
                    detail=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_TICKET"),
                )

            available_ticket = available_tickets.filter(expired_at__gte=date).order_by("expired_at").first()
            if available_ticket is None:
                raise ValidationException(
                    detail=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_TICKET"),
                )

            try:
                available_ticket.unused_count -= 1
                available_ticket.used_count += 1
                available_ticket.save(update_fields=["used_count", "unused_count", "updated_at", "version"])
                customer_tickets[available_ticket].append(date)
            except RecordModifiedError:
                raise ValidationException(
                    detail=SYSTEM_CODE.message("CONFLICT_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("CONFLICT_CUSTOMER_TICKET"),
                )

        return customer_tickets

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
        # 앞으로 예정된 날짜 목록(하원 날짜 포함)
        hotel_type_reserved_dates = self._reservation_selector.get_queryset_for_hotel_type_reservation(
            customer_id=customer.id,
            customer_pet_id=reservation_data["pet_id"],
            pet_kindergarden_id=pet_kindergarden.id,
        )
        hotel_type_full_reserved_dates = self.append_next_day_to_date_series(hotel_type_reserved_dates)

        # 일일 예약 현황 업데이트(등하원 날짜가 겹치는 연속된 예약은 1회로 처리)
        daily_reservation_dates = self.reservation_dates + [self.reservation_dates[-1] + timedelta(days=1)]
        hotel_type_full_reserved_dates_exclude_current_reservation = [
            date for date in daily_reservation_dates if date not in hotel_type_full_reserved_dates
        ]
        for date in daily_reservation_dates:
            if date not in hotel_type_full_reserved_dates_exclude_current_reservation:
                continue
            reserved_at = datetime.combine(date, pet_kindergarden.business_start_hour)
            daily_reservation, created = DailyReservation.objects.get_or_create(
                pet_kindergarden_id=pet_kindergarden.id,
                reserved_at=reserved_at,
                defaults={"total_pet_count": 1, "hotel_pet_count": 1},
            )
            if not created:
                DailyReservation.objects.filter(
                    pet_kindergarden_id=pet_kindergarden.id, reserved_at=reserved_at
                ).update(hotel_pet_count=F("hotel_pet_count") + 1, total_pet_count=F("total_pet_count") + 1)

    def create_reservations(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
        customer_tickets: Optional[dict[CustomerTicket, list[datetime]]] = None,
    ) -> list[Reservation]:
        """
        이 함수는 주어진 정보를 활용하여 여러 날짜에 걸친 예약을 생성합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력
            customer_tickets (Optional[dict[CustomerTicket, list[datetime]]]): 예약에 사용된 티켓 정보

        Returns:
            list[Reservation]: 생성된 예약 객체 리스트
        """
        if not customer_tickets:
            raise InvalidParameterFormatException(
                detail=SYSTEM_CODE.message("INVALID_PARAMETER_FORMAT"),
                code=SYSTEM_CODE.code("INVALID_PARAMETER_FORMAT"),
            )

        reservations = []
        reserved_at = datetime.combine(self.reservation_dates[0], pet_kindergarden.business_start_hour)
        end_at = self.reservation_dates[-1] + timedelta(days=1)
        parent_id = None
        depth = 0
        is_extented = True if len(customer_tickets) > 1 else False
        for ticket in customer_tickets:
            reservation = Reservation.objects.create(
                reserved_at=reserved_at,
                end_at=end_at,
                is_attended=None,
                reservation_status=ReservationStatus.COMPLETED.value,
                pet_kindergarden_id=pet_kindergarden.id,
                customer_id=customer.id,
                customer_pet_id=reservation_data["pet_id"],
                customer_ticket_id=ticket.id,
                parent_id=parent_id,
                depth=depth,
                is_extented=is_extented,
            )
            parent_id = reservation.id
            depth += 1
            reservations.append(reservation)

        return reservations

    def handle_tickets_usage(
        self,
        customer_tickets: dict[CustomerTicket, list[datetime]],
        reservations: list[Reservation],
    ) -> None:
        """
        이 함수는 고객 티켓 사용 로그를 생성합니다.

        Args:
            customer_tickets (dict[CustomerTicket, list[datetime]]): 예약에 사용된 티켓 정보
            reservations (list[Reservation]): 예약 객체

        Returns:
            None
        """
        for index, ticket in enumerate(customer_tickets):
            CustomerTicketUsageLog.objects.create(
                customer_ticket_id=ticket.id,
                reservation_id=reservations[index].id,
                used_count=len(customer_tickets[ticket]),
            )

    def get_reservation_info(
        self,
        reservation_data: dict[str, Any],
        customer_tickets: dict[CustomerTicket, list[datetime]],
    ) -> dict[str, Any]:
        """
        이 함수는 생성한 예약 정보를 반환합니다.

        Args:
            reservation_data (dict[str, Any]): 사용자 입력
            customer_tickets (dict[CustomerTicket, list[datetime]]): 고객 티켓 객체

        Returns:
            dict[str, Any]: 예약 정보 반환
        """
        unused_count = 0
        ticket_expiration_dates = []
        for customer_ticket in customer_tickets:
            count = self._customer_ticket_selector.get_by_customer_ticket_id_for_unused_count(customer_ticket.id)
            unused_count += count if count is not None else 0

            if customer_ticket.unused_count > 0:
                ticket_expiration_dates.append(customer_ticket.expired_at)

        pet_name = self._customer_pet_selector.get_by_pet_id_for_pet_name(reservation_data["pet_id"])
        reservation_info = {
            "attendance_date": reservation_data["reserved_date"],
            "end_date": reservation_data["end_date"],
            "usage_count": sum(len(tickets) for tickets in customer_tickets.values()),
            "remain_count": unused_count,
            "pet_name": pet_name,
            "ticket_type": reservation_data["ticket_type"],
            "ticket_expired_at": min(ticket_expiration_dates) if ticket_expiration_dates else None,
        }

        return reservation_info

    @staticmethod
    def append_next_day_to_date_series(date_strings: list[str]) -> list[datetime]:
        """
        이 함수는 연속된 날짜들을 찾아내고, 각 연속 구간의 끝에 하루를 추가합니다.

        Args:
            date_strings (list[str]): 고객 객체

        Returns:
            list[datetime]: DateTime 객체 리스트 반환
        """
        dates = sorted(datetime.strptime(date_str, "%Y-%m-%d") for date_str in date_strings)

        extended_dates = []
        for k, g in groupby(enumerate(dates), lambda x: x[0] - x[1].toordinal()):
            group = list(map(itemgetter(1), g))
            extended_dates.extend(group)
            extended_dates.append(group[-1] + timedelta(days=1))

        return extended_dates
