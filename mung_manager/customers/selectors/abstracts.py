from abc import ABC, abstractmethod
from typing import Optional

from django.db.models.query import QuerySet

from mung_manager.customers.models import Customer
from mung_manager.errors.exceptions import NotImplementedException


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
