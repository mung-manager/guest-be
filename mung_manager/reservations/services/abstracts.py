from abc import ABC, abstractmethod
from typing import Any

from django.db.models import QuerySet

from mung_manager.errors.exceptions import NotImplementedException


class AbstractReservationService(ABC):

    @abstractmethod
    def extract_available_reservation_dates(
        self,
        tickets: QuerySet[Any],
        day_off_dates: list[str],
        fully_booked_dates: list[str],
        start_date: str,
    ) -> list[dict[str, Any]]:
        raise NotImplementedException()
