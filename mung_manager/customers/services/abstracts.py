from abc import ABC, abstractmethod

from mung_manager.customers.models import Customer
from mung_manager.errors.exceptions import NotImplementedException


class AbstractCustomerService(ABC):

    @abstractmethod
    def register_customer(
        self,
        user,
        customer_id: int,
    ) -> Customer:
        raise NotImplementedException()
