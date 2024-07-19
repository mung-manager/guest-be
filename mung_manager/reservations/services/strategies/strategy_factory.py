from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerPetSelector,
    AbstractCustomerTicketSelector,
)
from mung_manager.reservations.selectors.abstracts import (
    AbstractDailyReservationSelector,
    AbstractReservationSelector,
)
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import (
    AbstractReservationStrategy,
)
from mung_manager.reservations.services.strategies.all_day_reservation_strategy import (
    AllDayReservationStrategy,
)
from mung_manager.reservations.services.strategies.hotel_reservation_strategy import (
    HotelReservationStrategy,
)
from mung_manager.reservations.services.strategies.time_reservation_strategy import (
    TimeReservationStrategy,
)
from mung_manager.tickets.enums import TicketType


class ReservationStrategyFactory:
    def __init__(
        self,
        customer_pet_selector: AbstractCustomerPetSelector,
        customer_ticket_selector: AbstractCustomerTicketSelector,
        daily_reservation_selector: AbstractDailyReservationSelector,
        reservation_selector: AbstractReservationSelector,
    ):
        self._customer_pet_selector = customer_pet_selector
        self._customer_ticket_selector = customer_ticket_selector
        self._daily_reservation_selector = daily_reservation_selector
        self._reservation_selector = reservation_selector

    def create_strategy(  # type: ignore
        self,
        ticket_type: str,
        reservation_service: AbstractReservationService,
    ) -> AbstractReservationStrategy:

        if ticket_type == TicketType.TIME.value:
            return TimeReservationStrategy(
                customer_pet_selector=self._customer_pet_selector,
                reservation_service=reservation_service,
                customer_ticket_selector=self._customer_ticket_selector,
                daily_reservation_selector=self._daily_reservation_selector,
                reservation_selector=self._reservation_selector,
            )
        elif ticket_type == TicketType.ALL_DAY.value:
            return AllDayReservationStrategy(
                customer_pet_selector=self._customer_pet_selector,
                reservation_service=reservation_service,
                customer_ticket_selector=self._customer_ticket_selector,
            )
        elif ticket_type == TicketType.HOTEL.value:
            return HotelReservationStrategy(
                customer_pet_selector=self._customer_pet_selector,
                reservation_service=reservation_service,
                customer_ticket_selector=self._customer_ticket_selector,
            )
