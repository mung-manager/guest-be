from mung_manager.reservations.selectors.abstracts import AbstractDayOffSelector
from typing import Optional

from django.db.models import CharField
from django.db.models.functions import Cast

from mung_manager.reservations.models import DayOff


class DayOffSelector(AbstractDayOffSelector):
    """
    이 클래스는 휴무일을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_pet_kindergarden_id_and_date_range_for_day_off(
            self, pet_kindergarden_id: int, date_range: list[str],
    ) -> list[Optional[str]]:
        """
        반려동물 유치원 아이디와 휴무일 날짜 범위로 휴무일 날짜 목록을 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            date_range (list[str]): 검색할 날짜 범위 (시작일, 종료일)

        Returns:
            list[Optional[str]]: 휴무일 날짜 리스트
        """
        day_off_dates = (
            DayOff.objects.filter(pet_kindergarden_id=pet_kindergarden_id, day_off_at__range=date_range)
            .annotate(day_off_at_str=Cast("day_off_at", CharField()))
            .values_list("day_off_at_str", flat=True)
        )

        return [date for date in day_off_dates]
