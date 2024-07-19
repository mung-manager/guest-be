from typing import Optional

from mung_manager.customers.selectors.customer_pets import CustomerPetSelector
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService

from mung_manager.reservations.services.strategies.abstract_strategy import AbstractReservationStrategy
from mung_manager.reservations.services.strategies.all_day_reservation_strategy import AllDayReservationStrategy
from mung_manager.reservations.services.strategies.hotel_reservation_strategy import HotelReservationStrategy
from mung_manager.reservations.services.strategies.time_reservation_strategy import TimeReservationStrategy
from mung_manager.tickets.enums import TicketType


class ReservationStrategyFactory:
    def __init__(
            self,
            customer_pet_selector: CustomerPetSelector,
            customer_ticket_selector: CustomerTicketSelector,
    ):
        self._customer_pet_selector = customer_pet_selector
        self._customer_ticket_selector = customer_ticket_selector

    def create_strategy(  # type: ignore
            self,
            ticket_type: str,
            reservation_service: AbstractReservationService,
    ) -> AbstractReservationStrategy:

        if ticket_type == TicketType.TIME.value:
            return TimeReservationStrategy(
                customer_pet_selector=self._customer_pet_selector,
                reservation_service=reservation_service,
                customer_ticket_selector=self._customer_ticket_selector
            )
        elif ticket_type == TicketType.ALL_DAY.value:
            return AllDayReservationStrategy(
                customer_pet_selector=self._customer_pet_selector,
                reservation_service=reservation_service,
                customer_ticket_selector=self._customer_ticket_selector
            )
        elif ticket_type == TicketType.HOTEL.value:
            return HotelReservationStrategy(
                customer_pet_selector=self._customer_pet_selector,
                reservation_service=reservation_service,
                customer_ticket_selector=self._customer_ticket_selector
            )
