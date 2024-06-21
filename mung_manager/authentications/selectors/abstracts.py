from abc import ABC, abstractmethod
from typing import Optional

from mung_manager.authentications.models import User
from mung_manager.errors.exceptions import NotImplementedException


class AbstractUserSelector(ABC):
    @abstractmethod
    def get_by_social_id(self, social_id: str) -> Optional[User]:
        raise NotImplementedException()
