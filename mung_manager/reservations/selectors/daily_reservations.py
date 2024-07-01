from typing import Optional

from django.db.models import DateField
from django.db.models.functions import Cast

from mung_manager.reservations.models import DailyReservation
from mung_manager.reservations.selectors.abstracts import (
    AbstractDailyReservationSelector,
)


class DailyReservationSelector(AbstractDailyReservationSelector):
    """
    이 클래스는 일별 예약을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_for_fully_booked(
        self,
        pet_kindergarden_id: int,
        date_range: list[str],
        daily_pet_limit: int,
    ) -> list[Optional[str]]:
        """
        반려동물 유치원 아이디와 예약일로 일별 예약 리스트를 조회하여 정원을 초과한 날짜를 반환합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            date_range (list[str]): 검색할 날짜 범위 (시작일, 종료일)
            daily_pet_limit (int): 하루 정원

        Returns:
            list[Optional[str]]: 정원이 초과한 날짜 리스트
        """
        if daily_pet_limit == -1:
            return []

        overbooked_dates = (
            DailyReservation.objects.filter(
                pet_kindergarden_id=pet_kindergarden_id,
                reserved_at__range=date_range,
                total_pet_count__gte=daily_pet_limit,
            )
            .annotate(reserved_at_str=Cast("reserved_at", DateField()))
            .values_list("reserved_at_str", flat=True)
        )

        return [date.strftime("%Y-%m-%d") for date in overbooked_dates]
