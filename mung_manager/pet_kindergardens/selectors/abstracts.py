from abc import ABC, abstractmethod
from typing import Any, Optional

from django.db.models import QuerySet
from typing_extensions import Annotated

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.pet_kindergardens.types import info_for_full_address


class AbstractPetKindergardenSelector(ABC):

    @abstractmethod
    def get_by_id_and_user_id(self, pet_kindergarden_id: int, user_id: int) -> Optional[PetKindergarden]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_user(self, user) -> QuerySet[Annotated[PetKindergarden, info_for_full_address], dict[str, Any]]:
        raise NotImplementedException()
