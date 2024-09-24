from datetime import date, datetime

from django.db.models.query import QuerySet
from django_stubs_ext import ValuesQuerySet

from mung_manager.reservations.selectors.abstracts import (
    AbstractDailyReservationSelector,
)
from mung_manager_db.models import DailyReservation


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

    def get_queryset_for_fully_booked(
        self,
        pet_kindergarden_id: int,
        date_range: list[datetime],
        daily_pet_limit: int,
    ) -> ValuesQuerySet[DailyReservation, date] | None:
        """
        반려동물 유치원 아이디와 예약일로 일별 예약 리스트를 조회하여 정원을 초과한 날짜를 반환합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            date_range (list[str]): 검색할 날짜 범위 (시작일, 종료일)
            daily_pet_limit (int): 하루 정원

        Returns:
            ValuesQuerySet[DailyReservation, date] | None: 정원이 초과한 날짜 목록 쿼리셋
        """
        if daily_pet_limit == -1:
            return None

        return DailyReservation.objects.filter(
            pet_kindergarden_id=pet_kindergarden_id,
            reserved_at__range=date_range,
            total_pet_count__gte=daily_pet_limit,
        ).values_list("reserved_at", flat=True)

    def get_queryset_by_pet_kindergarden_id_and_reserved_at(
        self, pet_kindergarden_id: int, reserved_at: str
    ) -> QuerySet[DailyReservation]:
        """
        반려동물 유치원 아이디와 예약일로 일별 예약 리스트를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reserved_at (str): 예약일

        Returns:
            QuerySet[DailyReservation]: 일별 예약 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return DailyReservation.objects.filter(pet_kindergarden_id=pet_kindergarden_id, reserved_at=reserved_at)
