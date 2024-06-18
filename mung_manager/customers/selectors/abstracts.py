from abc import ABC, abstractmethod
from typing import List, Optional

from django.db.models.query import QuerySet

from mung_manager.customers.models import (
    Customer,
    CustomerPet,
    CustomerTicket,
    CustomerTicketRegistrationLog,
    CustomerTicketUsageLog,
)
from mung_manager.errors.exceptions import NotImplementedException


class AbstractCustomerSelector(ABC):
    @abstractmethod
    def get_by_filter_for_search(self, filters: Optional[dict] = None) -> QuerySet[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def get_with_undeleted_customer_pet_by_id(self, customer_id: int) -> Optional[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_id(self, customer_id: int) -> bool:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_pet_kindergarden_id_and_phone_number(self, pet_kindergarden_id: int, phone_number: str) -> bool:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_pet_kindergarden_id(self, pet_kindergarden_id: int) -> QuerySet[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_id_and_customer_pet_id_for_undeleted_customer_pets(
        self,
        customer_id: int,
        customer_pet_id: int,
    ) -> Optional[Customer]:
        raise NotImplementedException()


class AbstractCustomerTicketSelector(ABC):
    @abstractmethod
    def get_queryset_by_customer_id_for_ticket_type(self, customer_id: int) -> dict[str, list]:
        raise NotImplementedException()

    @abstractmethod
    def get_with_ticket_by_id_and_customer_id(
        self, customer_ticket_id: int, customer_id: int
    ) -> Optional[CustomerTicket]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_for_hotel(self, customer_ticket_ids: list[int], customer_id: int) -> QuerySet[CustomerTicket]:
        raise NotImplementedException()


class AbstractCustomerPetSelector(ABC):
    @abstractmethod
    def get_queryset_by_names_and_customer_id_for_undeleted_customer_pet(
        self, names: List[str], customer_id: int
    ) -> QuerySet[CustomerPet]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_names_and_customer_id_for_undeleted_customer_pet(self, names: List[str], customer_id: int) -> bool:
        raise NotImplementedException()

    @abstractmethod
    def get_by_keyword_for_search(self, keyword: str) -> QuerySet[CustomerPet]:
        raise NotImplementedException()


class AbstractCustomerTicketUsageLogSelector(ABC):
    @abstractmethod
    def get_queryset_by_customer_id_for_ticket_usage_logs(self, customer_id: int) -> QuerySet[CustomerTicketUsageLog]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_reservation_ids(self, reservation_ids: list[int]) -> QuerySet[CustomerTicketUsageLog]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_reservation_id(self, reservation_id: int) -> Optional[CustomerTicketUsageLog]:
        raise NotImplementedException()


class AbstractCustomerTicketRegistrationLogSelector(ABC):
    @abstractmethod
    def get_queryset_by_customer_id_for_ticket_registration_logs(
        self, customer_id: int
    ) -> QuerySet[CustomerTicketRegistrationLog]:
        raise NotImplementedException()
