from typing import Optional

from django.db.models import DateField
from django.db.models.functions import Cast
from django.db.models.query import QuerySet

from mung_manager.reservations.models import DailyReservation
from mung_manager.reservations.selectors.abstracts import (
    AbstractDailyReservationSelector,
)


class DailyReservationSelector(AbstractDailyReservationSelector):
    """이 클래스는 일별 예약을 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_year_and_month_and_pet_kindergarden_id(
        self, year: int, month: int, pet_kindergarden_id: int
    ) -> QuerySet[DailyReservation]:
        """년도와 월과 반려동물 유치원 아이디로 일별 예약 리스트를 조회합니다.

        Args:
            year (int): 년도
            month (int): 월
            pet_kindergarden_id (int): 반려동물 유치원 아이디

        Returns:
            QuerySet[DailyReservation]: 일별 예약 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return DailyReservation.objects.filter(
            reserved_at__year=year, reserved_at__month=month, pet_kindergarden_id=pet_kindergarden_id
        )

    def get_queryset_by_pet_kindergarden_id_and_reserved_at(
        self, pet_kindergarden_id: int, reserved_at: str
    ) -> QuerySet[DailyReservation]:
        """반려동물 유치원 아이디와 예약일로 일별 예약 리스트를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reserved_at (str): 예약일

        Returns:
            QuerySet[DailyReservation]: 일별 예약 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return DailyReservation.objects.filter(pet_kindergarden_id=pet_kindergarden_id, reserved_at=reserved_at)

    def get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
        self, pet_kindergarden_id: int, reserved_at: str, end_at: str
    ) -> QuerySet[DailyReservation]:
        """반려동물 유치원 아이디와 예약일과 종료일로 일별 예약 리스트를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reserved_at (str): 예약일
            end_at (str): 종료일

        Returns:
            QuerySet[DailyReservation]: 일별 예약 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return DailyReservation.objects.filter(
            pet_kindergarden_id=pet_kindergarden_id, reserved_at__range=[reserved_at, end_at]
        )

    def get_queryset_for_overregistered(
        self, pet_kindergarden_id: int, reserved_at: list[str], daily_pet_limit: int
    ) -> list[Optional[str]]:
        """반려동물 유치원 아이디와 예약일로 일별 예약 리스트를 조회하여 정원을 초과한 날짜를 반환합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reserved_at (list[str]): 예약일 리스트 (예약일, 종료일)
            daily_pet_limit (int): 하루 정원

        Returns:
            list[str]: 정원이 초과한 날짜 리스트
        """
        if daily_pet_limit == -1:
            return []

        overbooked_dates = (
            DailyReservation.objects.filter(
                pet_kindergarden_id=pet_kindergarden_id,
                reserved_at__range=reserved_at,
                total_pet_count__gte=daily_pet_limit,
            )
            .annotate(reserved_at_str=Cast("reserved_at", DateField()))
            .values_list("reserved_at_str", flat=True)
        )

        return [date.strftime("%Y-%m-%d") for date in overbooked_dates]
