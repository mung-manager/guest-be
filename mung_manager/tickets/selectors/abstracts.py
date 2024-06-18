from abc import ABC, abstractmethod
from typing import Optional

from django.db.models.query import QuerySet

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.tickets.models import Ticket


class AbstractTicketSelector(ABC):
    @abstractmethod
    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_pet_kindergarden_id(self, pet_kindergarden_id: int) -> QuerySet[Ticket]:
        raise NotImplementedException()

    @abstractmethod
    def get_querset_by_pet_kindergarden_id_for_undeleted_ticket(self, pet_kindergarden_id: int) -> QuerySet[Ticket]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_id_for_undeleted_ticket(self, ticket_id: int) -> Optional[Ticket]:
        raise NotImplementedException()
