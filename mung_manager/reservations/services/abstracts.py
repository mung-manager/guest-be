from abc import ABC, abstractmethod

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.reservations.models import DayOff, Reservation


class AbstractDayOffService(ABC):
    @abstractmethod
    def create_day_off(self, pet_kindergarden_id: int, day_off_at: str, user) -> DayOff:
        raise NotImplementedException()

    @abstractmethod
    def delete_day_off(self, pet_kindergarden_id: int, day_off_id: int, user) -> None:
        raise NotImplementedException()


class AbstractReservationService(ABC):
    @abstractmethod
    def toggle_reservation_is_attended(self, pet_kindergarden_id: int, reservation_id: int, user) -> Reservation:
        raise NotImplementedException()

    # @abstractmethod
    # def create_reservation(
    #     self,
    #     pet_kindergarden_id: int,
    #     customer_ticket_id: int,
    #     customer_id: int,
    #     customer_pet_id: int,
    #     reserved_at: str,
    #     end_at: str,
    #     user,
    # ) -> Reservation:
    #     raise NotImplementedException()
