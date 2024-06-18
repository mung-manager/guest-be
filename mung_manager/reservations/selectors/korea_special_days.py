from django.db.models.query import QuerySet

from mung_manager.reservations.models import KoreaSpecialDay
from mung_manager.reservations.selectors.abstracts import (
    AbstractKoreaSpecialDaySelector,
)


class KoreaSpecialDaySelector(AbstractKoreaSpecialDaySelector):
    """이 클래스는 한국의 공휴일을 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_year_and_month(self, year: int, month: int) -> QuerySet[KoreaSpecialDay]:
        """년도와 월로 공휴일 리스트를 조회합니다.

        Args:
            year (int): 년도
            month (int): 월

        Returns:
            QuerySet[DayOff]: 공휴일 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return KoreaSpecialDay.objects.filter(special_day_at__year=year, special_day_at__month=month)
