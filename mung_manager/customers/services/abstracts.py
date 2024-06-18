from abc import ABC, abstractmethod
from typing import List, Optional

from django.core.files.uploadedfile import InMemoryUploadedFile

from mung_manager.customers.models import Customer, CustomerTicket
from mung_manager.errors.exceptions import NotImplementedException


class AbstractCustomerService(ABC):
    @abstractmethod
    def create_customer(
        self,
        user,
        pet_kindergarden_id: int,
        name: str,
        phone_number: str,
        pets: List[str],
    ) -> Customer:
        raise NotImplementedException()

    @abstractmethod
    def create_customers_by_csv(self, user, pet_kindergarden_id: int, csv_file: InMemoryUploadedFile) -> List[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def toggle_customer_is_active(self, user, customer_id: int, pet_kindergarden_id: int) -> Customer:
        raise NotImplementedException()

    @abstractmethod
    def update_customer(
        self,
        user,
        pet_kindergarden_id: int,
        customer_id: int,
        name: str,
        phone_number: str,
        pets_to_add: List[str],
        pets_to_delete: List[str],
        memo: str,
    ) -> Optional[Customer]:
        raise NotImplementedException()


class AbstractCustomerTicketService(ABC):
    @abstractmethod
    def register_ticket(self, user, customer_id: int, pet_kindergarden_id: int, ticket_id: int) -> CustomerTicket:
        raise NotImplementedException()
