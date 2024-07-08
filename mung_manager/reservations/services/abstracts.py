from abc import ABC, abstractmethod

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.reservations.models import Reservation


class AbstractReservationService(ABC):

    @abstractmethod
    def cancel_reservation(self, reservation: Reservation) -> None:
        raise NotImplementedException()
