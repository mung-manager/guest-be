from concurrency.exceptions import RecordModifiedError
from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone
from requests import Request

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.customers.selectors.customer_ticket_usage_logs import (
    CustomerTicketUsageLogSelector,
)
from mung_manager.errors.exceptions import ValidationException
from mung_manager.pet_kindergardens.enums import ReservationChangeOption
from mung_manager.reservations.enums import ReservationStatus
from mung_manager.reservations.models import Reservation
from mung_manager.reservations.selectors.daily_reservations import (
    DailyReservationSelector,
)
from mung_manager.reservations.selectors.reservations import ReservationSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.tickets.enums import TicketType


class ReservationService(AbstractReservationService):
    """
    이 클래스는 예약과 관련된 비즈니스 로직을 담당합니다.
    """

    def __init__(
        self,
        reservation_selector: ReservationSelector,
        customer_ticket_usage_log_selector: CustomerTicketUsageLogSelector,
        daily_reservation_selector: DailyReservationSelector,
    ):
        self._reservation_selector = reservation_selector
        self._daily_reservation_selector = daily_reservation_selector
        self._customer_ticket_usage_log_selector = customer_ticket_usage_log_selector

    @staticmethod
    def validate_reservation_cancellation(request: Request, reservation: Reservation) -> None:
        """
        이 함수는 당일 취소 불가능 옵션이면서 취소하려는 예약 날짜가 오늘일 때를 검증합니다.

        Args:
            request (Request): request 객체
            reservation (Reservation): 예약 객체

        Returns:
            None
        """
        if request.pet_kindergarden.reservation_change_option == ReservationChangeOption.SAME_DAY_UNCHANGE.value:
            if reservation.reserved_at.date() == timezone.now().date():
                raise ValidationException(
                    detail=SYSTEM_CODE.message("CANNOT_CANCEL_RESERVATION"),
                    code=SYSTEM_CODE.code("CANNOT_CANCEL_RESERVATION"),
                )

    @transaction.atomic
    def cancel_reservation(self, reservation: Reservation) -> None:
        """
        이 함수는 reservation 객체에 해당하는 예약을 취소하고 필요 시 티켓의 횟수를 복구합니다.

        Args:
            reservation (Reservation): 예약 객체

        Returns:
            None
        """
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
        reservation_ids = list(reservations.values_list('id', flat=True))
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
