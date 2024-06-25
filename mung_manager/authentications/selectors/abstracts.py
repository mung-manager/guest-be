from abc import ABC, abstractmethod
from typing import Optional

from mung_manager.authentications.models import User
from mung_manager.errors.exceptions import NotImplementedException


class AbstractUserSelector(ABC):
    @abstractmethod
    def get_by_social_id(self, social_id: str) -> Optional[User]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_user_id_and_group_id(self, user_id: int, partner_group_id: int, guest_group_id: int) -> bool:
        raise NotImplementedException()
