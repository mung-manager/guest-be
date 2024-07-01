from abc import ABC, abstractmethod
from typing import Any

from django.db.models.query import QuerySet

from mung_manager.errors.exceptions import NotImplementedException


class AbstractPetKindergardenSelector(ABC):

    @abstractmethod
    def get_queryset_by_user(
        self,
        user,
    ) -> QuerySet[Any]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_kindergarden_id_for_reservation_availability_option(self, pet_kindergarden_id: str) -> QuerySet[Any]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_kindergarden_id_for_daily_pet_limit(self, pet_kindergarden_id: str) -> int:
        raise NotImplementedException()
