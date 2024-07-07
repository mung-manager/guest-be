from abc import ABC, abstractmethod
from typing import Annotated, Any

from django.db.models import QuerySet

from mung_manager.customers.models import Customer
from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden
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
