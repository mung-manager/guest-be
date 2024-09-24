from abc import ABC, abstractmethod
from typing import Any, Optional

from django.db.models import QuerySet
from django_stubs_ext import ValuesQuerySet
from typing_extensions import Annotated

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.types import full_address_type
from mung_manager_db.models import PetKindergarden


class AbstractPetKindergardenSelector(ABC):

    @abstractmethod
    def get_by_id_and_user_id(self, pet_kindergarden_id: int, user_id: int) -> Optional[PetKindergarden]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_user(self, user) -> QuerySet[Annotated[PetKindergarden, full_address_type], dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_kindergarden_id_for_reservation_availability_option(
        self, pet_kindergarden_id: int
    ) -> ValuesQuerySet[PetKindergarden, str]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_kindergarden_id_for_daily_pet_limit(self, pet_kindergarden_id: int) -> int:
        raise NotImplementedException()
