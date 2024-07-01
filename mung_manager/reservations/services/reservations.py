from datetime import datetime, timedelta
from typing import Any

from django.db.models import QuerySet

from mung_manager.reservations.services.abstracts import AbstractReservationService


class ReservationService(AbstractReservationService):
    """
    이 클래스는 예약을 DB에 PUSH하는 비즈니스 로직을 담당합니다.
    """

    def extract_available_reservation_dates(
        self,
        tickets: QuerySet[Any],
        day_off_dates: list[str],
        fully_booked_dates: list[str],
        start_date: str,
    ) -> list[dict[str, Any]]:
        """
        휴무일 날짜 범위와 반려동물 유치원 아이디로 휴무일 날짜 목록을 조회합니다.

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
