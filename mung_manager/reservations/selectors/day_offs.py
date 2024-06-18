from typing import Optional

from django.db.models import DateField
from django.db.models.functions import Cast
from django.db.models.query import QuerySet

from mung_manager.reservations.models import DayOff
from mung_manager.reservations.selectors.abstracts import AbstractDayOffSelector


class DayOffSelector(AbstractDayOffSelector):
    """이 클래스는 휴무일을 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_pet_kindergarden_id_and_day_off_at(
        self, pet_kindergarden_id: int, year: int, month: int
    ) -> QuerySet[DayOff]:
        """반려동물 유치원 아이디와 년도와 월로 휴무일 리스트를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            year (int): 년도
            month (int): 월

        Returns:
            QuerySet[DayOff]: 휴무일 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return DayOff.objects.filter(
            pet_kindergarden_id=pet_kindergarden_id, day_off_at__year=year, day_off_at__month=month
        )

    def get_by_id(self, day_off_id: int) -> Optional[DayOff]:
        """휴무일 아이디로 휴무일을 조회합니다.

        Args:
            day_off_id (int): 휴무일 아이디

        Returns:
            Optional[DayOff]: 휴무일이 존재하면 휴무일 객체를 반환하고, 존재하지 않으면 None을 반환
        """
        try:
            return DayOff.objects.filter(id=day_off_id).get()
        except DayOff.DoesNotExist:
            return None

    def exists_by_day_off_at_and_pet_kindergarden_id(self, day_off_at: str, pet_kindergarden_id: int) -> bool:
        """휴무일 날짜와 반려동물 유치원 아이디로 휴무일이 존재하는지 확인합니다.

        Args:
            day_off_at (str): 휴무일 날짜
            pet_kindergarden_id (int): 반려동물 유치원 아이디

        Returns:
            bool: 휴무일이 존재하면 True를 반환하고, 존재하지 않으면 False를 반환
        """
        return DayOff.objects.filter(day_off_at=day_off_at, pet_kindergarden_id=pet_kindergarden_id).exists()

    def get_queryset_by_pet_kindergarden_id_and_day_off_at_for_day_offs(
        self, pet_kindergarden_id: int, day_off_at: list[str]
    ) -> list[Optional[str]]:
        """휴무일 날짜 범위와 반려동물 유치원 아이디로 휴무일이 존재하는 날짜들을 반환합니다.

        Args:
            date_range (list[str]): 휴무일 날짜 범위 (시작일, 종료일)
            pet_kindergarden_id (int): 반려동물 유치원 아이디

        Returns:
            list[str]: 휴무일이 존재하는 날짜 리스트
        """
        day_off_dates = (
            DayOff.objects.filter(pet_kindergarden_id=pet_kindergarden_id, day_off_at__range=day_off_at)
            .annotate(day_off_at_str=Cast("day_off_at", DateField()))
            .values_list("day_off_at_str", flat=True)
        )

        return [date.strftime("%Y-%m-%d") for date in day_off_dates]
