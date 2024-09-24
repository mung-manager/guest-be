from datetime import date, datetime

from django_stubs_ext import ValuesQuerySet

from mung_manager.reservations.selectors.abstracts import AbstractDayOffSelector
from mung_manager_db.models import DayOff


class DayOffSelector(AbstractDayOffSelector):
    """
    이 클래스는 휴무일을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_pet_kindergarden_id_and_date_range_for_day_off(
        self,
        pet_kindergarden_id: int,
        date_range: list[datetime],
    ) -> ValuesQuerySet[DayOff, date]:
        """
        반려동물 유치원 아이디와 휴무일 날짜 범위로 휴무일 날짜 목록을 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            date_range (list[datetime]): 검색할 날짜 범위 (시작일, 종료일)

        Returns:
            ValuesQuerySet[DayOff, date]: 존재하지 않으면 빈 쿼리셋 반환
        """

        return DayOff.objects.filter(pet_kindergarden_id=pet_kindergarden_id, day_off_at__range=date_range).values_list(
            "day_off_at", flat=True
        )
