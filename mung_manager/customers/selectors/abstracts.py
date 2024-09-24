from abc import ABC, abstractmethod
from typing import Annotated, Any, Optional

from django.db.models.query import QuerySet

from mung_manager.customers.types import is_expired_type
from mung_manager.errors.exceptions import NotImplementedException
from mung_manager_db.models import (
    Customer,
    CustomerPet,
    CustomerTicket,
    CustomerTicketUsageLog,
    User,
)


class AbstractCustomerSelector(ABC):

    @abstractmethod
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_phone_number_and_user_id_is_null(
        self,
        phone_number: str,
    ) -> QuerySet[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_user_and_pet_kindergarden_id(self, user, pet_kindergarden_id: int) -> bool:
        raise NotImplementedException()

    @abstractmethod
    def get_by_user_and_pet_kindergarden_id_for_active_customer(
        self, user, pet_kindergarden_id: int
    ) -> Optional[Customer]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_user_and_pet_kindergarden_id(self, user: User, pet_kindergarden_id: int) -> Optional[Customer]:
        raise NotImplementedException()


class AbstractCustomerPetSelector(ABC):
    @abstractmethod
    def get_queryset_by_customer(self, customer: Customer) -> QuerySet[CustomerPet]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_customer_and_pet_id(self, customer: Customer, pet_id: int) -> bool:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_id_for_pet_name(self, pet_id: int) -> Optional[str]:
        raise NotImplementedException()


class AbstractCustomerTicketSelector(ABC):
    @abstractmethod
    def get_queryset_by_customer(self, customer: Customer) -> dict[str, QuerySet]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_customer_and_ticket_type_for_ticket_detail(
        self, customer: Customer, ticket_type: str
    ) -> QuerySet[CustomerTicket]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_customer_for_count(self, customer: Customer) -> dict[str, int]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_customer_for_parchase_list(
        self, customer: Customer
    ) -> QuerySet[Annotated[CustomerTicket, is_expired_type], dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_customer_for_hotel_ticket_type(self, customer: Customer) -> QuerySet[CustomerTicket]:
        raise NotImplementedException()

    @abstractmethod
    def get_for_all_day_or_time_ticket_type(
        self, customer: Customer, ticket_type: str, ticket_id: Optional[int]
    ) -> Optional[CustomerTicket]:
        raise NotImplementedException()

    @abstractmethod
    def get_with_ticket_by_id_and_customer_id(
        self, customer_ticket_id: int, customer_id: int
    ) -> Optional[CustomerTicket]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_customer_ticket_id_for_unused_count(self, customer_ticket_id: int) -> Optional[int]:
        raise NotImplementedException()


class AbstractCustomerTicketUsageLogSelector(ABC):

    @abstractmethod
    def get_queryset_by_reservation_ids(self, reservation_ids: list[int]) -> QuerySet[CustomerTicketUsageLog]:
        raise NotImplementedException()
