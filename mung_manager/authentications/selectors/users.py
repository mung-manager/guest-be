from typing import Optional

from mung_manager.authentications.models import User
from mung_manager.authentications.selectors.abstracts import AbstractUserSelector


class UserSelector(AbstractUserSelector):
    """
    이 클래스는 유저를 DB에 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_by_social_id(self, social_id: str) -> Optional[User]:
        """
        이 함수는 소셜 아이디로 유저를 조회합니다.

        Args:
            social_id (str): 소셜 아이디

        Returns:
            Optional[User]: 유저 객체
        """
        try:
            return User.objects.filter(social_id=social_id).get()
        except User.DoesNotExist:
            return None

    def exists_by_user_id_and_group_id_for_group(
        self, user_id: int, partner_group_id: int, guest_group_id: int
    ) -> bool:
        """
        이 함수는 유저 아이디와 그룹 아이디로 해당 유저가 게스트가 아니면서 파트너인지 확인합니다.

        Args:
            user_id (int): 유저 아이디
            partner_group_id (int): 파트너 그룹 아이디
            guest_group_id (int): 게스트 그룹 아이디

        Returns:
            bool: 파트너 그룹에 속해 있으면 True, 아니면 False를 반환
        """
        return User.objects.filter(id=user_id, groups__id=partner_group_id).exclude(groups__id=guest_group_id).exists()

    def exists_by_user_id_and_group_id_for_permission(self, user_id: int, group_id: int) -> bool:
        """
        이 함수는 유저 아이디와 그룹 아이디로 해당 유저가 게스트인지 확인합니다.

        Args:
            user_id (int): 유저 아이디
            group_id (int): 게스트 그룹 아이디

        Returns:
            bool: 게스트이면 True, 아니면 False를 반환
        """
        return User.objects.filter(id=user_id, groups__id=group_id).exists()
