from datetime import datetime

from django.db.models.query import QuerySet

from mung_manager.reservations.models import DailyReservation
from mung_manager.reservations.selectors.abstracts import (
    AbstractDailyReservationSelector,
)


class DailyReservationSelector(AbstractDailyReservationSelector):
    """
    이 클래스는 일별 예약을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
        self, pet_kindergarden_id: int, reserved_at: datetime, end_at: datetime | None
    ) -> QuerySet[DailyReservation]:
        """
        반려동물 유치원 아이디와 예약일과 종료일로 일별 예약 리스트를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reserved_at (datetime): 예약일
            end_at (datetime): 종료일

        Returns:
            QuerySet[DailyReservation]: 일별 예약 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        reserved_at_str = reserved_at.strftime("%Y-%m-%d")
        end_at_str = end_at.strftime("%Y-%m-%d") if end_at else None

        return DailyReservation.objects.filter(
            pet_kindergarden_id=pet_kindergarden_id, reserved_at__range=[reserved_at_str, end_at_str]
        )
