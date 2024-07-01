from abc import ABC, abstractmethod
from typing import Optional

from mung_manager.errors.exceptions import NotImplementedException


class AbstractReservationSelector(ABC):
    pass


class AbstractDayOffSelector(ABC):
    @abstractmethod
    def get_queryset_by_pet_kindergarden_id_and_date_range_for_day_off(
        self,
        pet_kindergarden_id: int,
        date_range: list[str],
    ) -> list[Optional[str]]:
        raise NotImplementedException()


class AbstractDailyReservationSelector(ABC):
    @abstractmethod
    def get_queryset_for_fully_booked(
        self,
        pet_kindergarden_id: int,
        date_range: list[str],
        daily_pet_limit: int,
    ) -> list[Optional[str]]:
        raise NotImplementedException()
