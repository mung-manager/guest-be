from abc import ABC, abstractmethod
from typing import Any

from django.db.models import QuerySet
from django_stubs_ext import ValuesQuerySet, WithAnnotations

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    info_for_full_address,
)
from mung_manager.pet_kindergardens.types import info_for_summary


class AbstractPetKindergardenSelector(ABC):

    @abstractmethod
    def get_queryset_by_user(
        self, user
    ) -> QuerySet[WithAnnotations[PetKindergarden, info_for_full_address], dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_kindergarden_id_for_summary_info(
        self, pet_kindergarden_id: int
    ) -> ValuesQuerySet[PetKindergarden, info_for_summary]:
        raise NotImplementedException()
