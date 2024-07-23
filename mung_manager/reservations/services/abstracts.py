from abc import ABC, abstractmethod
from datetime import datetime, time
from typing import Optional

from django.db.models import QuerySet

from mung_manager.customers.models import Customer
from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden


class AbstractReservationService(ABC):

    @abstractmethod
    def cancel_reservation(self, pet_kindergarden: PetKindergarden, reservation_id: int) -> None:
        raise NotImplementedException()

    @abstractmethod
    def get_associated_reservation_ids_by_reservation_id(self, reservation_id: int) -> list[int]:
        raise NotImplementedException()

    @abstractmethod
    def get_available_timeslots(self, business_start_hour: time, business_end_hour: time, usage_time: int) -> list[str]:
        raise NotImplementedException()

    @abstractmethod
    def filter_available_reservation_dates(
        self,
        start_date: datetime,
        end_date: datetime,
        day_off_dates_queryset: QuerySet,
        fully_booked_dates_queryset: QuerySet,
    ) -> list[str]:
        raise NotImplementedException()

    @abstractmethod
    def get_available_reservation_dates(
        self, pet_kindergarden_id: int, customer: Customer, ticket_type: str, ticket_id: Optional[int]
    ) -> list[str]:
        raise NotImplementedException()

    @abstractmethod
    def register_reservation(
        self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict
    ) -> dict:
        raise NotImplementedException()
