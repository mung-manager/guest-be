from typing import Optional

from mung_manager.authentications.models import User
from mung_manager.authentications.selectors.abstracts import AbstractUserSelector


class UserSelector(AbstractUserSelector):
    """이 클래스는 유저를 DB에 PULL하는 비즈니스 로직을 담당합니다."""

    def get_by_social_id(self, social_id: str) -> Optional[User]:
        """이 함수는 소셜 아이디로 유저를 조회합니다.

        Args:
            social_id (str): 소셜 아이디

        Returns:
            Optional[User]: 유저 객체
        """
        try:
            return User.objects.filter(social_id=social_id).get()
        except User.DoesNotExist:
            return None
