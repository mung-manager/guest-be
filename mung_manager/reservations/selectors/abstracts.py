from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, Annotated

from django.db.models import QuerySet

from mung_manager.customers.models import Customer
from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.models import DailyReservation, Reservation
from mung_manager.reservations.models import Reservation
from mung_manager.reservations.types import attendance_type


class AbstractReservationSelector(ABC):

    @abstractmethod
    def get_queryset_by_customer_and_pet_kindergarden(
        self, customer: Customer, pet_kindergarden: PetKindergarden
    ) -> list[dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_customer_and_pet_kindergarden_for_detail(
        self, customer: Customer, pet_kindergarden: PetKindergarden, ticket_status: str
    ) -> QuerySet[Annotated[Reservation, attendance_type]] | list[dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_id_for_uncanceled_reservation(self, reservation_id: int) -> Optional[Reservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_child_ids_by_parent_id(self, parent_id: int) -> list[tuple[int, None]]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_with_customer_ticket_and_ticket_by_ids(self, reservation_ids: list[int]) -> QuerySet[Reservation]:
        raise NotImplementedException()


class AbstractDailyReservationSelector(ABC):
    @abstractmethod
    def get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
        self, pet_kindergarden_id: int, reserved_at: datetime, end_at: datetime | None
    ) -> QuerySet[DailyReservation]:
        raise NotImplementedException()
