from abc import ABC, abstractmethod
from typing import Optional

from mung_manager.authentications.models import User
from mung_manager.errors.exceptions import NotImplementedException


class AbstractUserSelector(ABC):
    @abstractmethod
    def get_by_social_id(self, social_id: str) -> Optional[User]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_email_excluding_self(
        self,
        user,
        email: Optional[str] = None,
    ) -> bool:
        raise NotImplementedException()
