from abc import ABC, abstractmethod

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager_db.models import Customer


class AbstractCustomerService(ABC):

    @abstractmethod
    def register_customer(
        self,
        user,
        customer_id: int,
    ) -> Customer:
        raise NotImplementedException()
