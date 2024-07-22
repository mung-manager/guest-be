from abc import ABC, abstractmethod

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.customers.models import Customer, CustomerTicket
from mung_manager.customers.selectors.abstracts import AbstractCustomerPetSelector
from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.models import Reservation
from mung_manager.reservations.services.abstracts import AbstractReservationService


class AbstractReservationStrategy(ABC):

    def __init__(
        self,
        customer_pet_selector: AbstractCustomerPetSelector,
        reservation_service: AbstractReservationService,
    ):
        self._customer_pet_selector = customer_pet_selector
        self._reservation_service = reservation_service

    def validate(self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict) -> None:

        self.common_validation(customer, pet_kindergarden, reservation_data)
        self.specific_validation(customer, pet_kindergarden, reservation_data)

    def common_validation(self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict) -> None:

        # 해당 반려동물이 해당 고객에게 속해있는지 검증
        check_object_or_not_found(
            self._customer_pet_selector.exists_by_customer_and_pet_id(
                customer=customer, pet_id=reservation_data["pet_id"]
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_PET"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_PET"),
        )

    @abstractmethod
    def specific_validation(
        self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict
    ) -> None:
        raise NotImplementedException()

    def reserve(self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict) -> None:
        customer_tickets = self.get_customer_tickets(customer, reservation_data)
        self.handle_daily_reservations(pet_kindergarden, reservation_data, customer)
        reservations = self.create_reservations(customer, pet_kindergarden, reservation_data, customer_tickets)
        self.handle_tickets_usage(customer_tickets, reservations)

    @abstractmethod
    def get_customer_tickets(self, customer: Customer, reservation_data: dict) -> CustomerTicket | list[CustomerTicket]:
        raise NotImplementedException()

    @abstractmethod
    def create_reservations(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict,
        customer_tickets: CustomerTicket | list[CustomerTicket],
    ) -> Reservation | list[Reservation]:
        raise NotImplementedException()

    @abstractmethod
    def handle_daily_reservations(
        self, pet_kindergarden: PetKindergarden, reservation_data: dict, customer: Customer
    ) -> None:
        raise NotImplementedException()

    @abstractmethod
    def handle_tickets_usage(
        self,
        customer_tickets: CustomerTicket | list[CustomerTicket],
        reservations: Reservation | list[Reservation],
    ) -> None:
        raise NotImplementedException()
