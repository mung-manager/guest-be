from abc import ABC, abstractmethod

from django.db.models import QuerySet

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.tickets.models import Ticket


class AbstractTicketSelector(ABC):

    @abstractmethod
    def get_querset_by_pet_kindergarden_id_for_undeleted_ticket(self, pet_kindergarden_id: int) -> QuerySet[Ticket]:
        raise NotImplementedException()
