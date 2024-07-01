from abc import ABC, abstractmethod
from typing import Any, Optional

from django.db.models import QuerySet

from mung_manager.customers.models import Customer
from mung_manager.errors.exceptions import NotImplementedException


class AbstractReservationService(ABC):

    @abstractmethod
    def extract_available_reservation_dates(
        self,
        tickets: QuerySet[Any],
        day_off_dates: list[Optional[str]],
        fully_booked_dates: list[Optional[str]],
        start_date: str,
    ) -> list[dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def calculate_available_reservation_dates(
        self, pet_kindergarden_id: int, customer: Customer, ticket_type: str
    ) -> list[dict[str, Any]]:
        raise NotImplementedException()
