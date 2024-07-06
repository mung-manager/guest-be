from abc import ABC, abstractmethod
from typing import Any

from mung_manager.customers.models import Customer
from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden


class AbstractReservationSelector(ABC):

    @abstractmethod
    def get_queryset_by_customer_and_pet_kindergarden(
        self, customer: Customer, pet_kindergarden: PetKindergarden
    ) -> list[dict[str, Any]]:
        raise NotImplementedException()
