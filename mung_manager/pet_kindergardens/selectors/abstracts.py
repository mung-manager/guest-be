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
