from abc import ABC, abstractmethod

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden


class AbstractReservationService(ABC):

    @abstractmethod
    def cancel_reservation(self, pet_kindergarden: PetKindergarden, reservation_id: int) -> None:
        raise NotImplementedException()

    @abstractmethod
    def get_associated_reservation_ids_by_reservation_id(self, reservation_id: int) -> list[int]:
        raise NotImplementedException()
