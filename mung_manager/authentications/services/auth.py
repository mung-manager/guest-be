from typing import Tuple

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from mung_manager.authentications.services.abstracts import AbstractAuthService
from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.errors.exceptions import AuthenticationFailedException
from mung_manager_db.models import User


class AuthService(AbstractAuthService):
    """
    이 클래스는 인증과 관련된 비즈니스 로직을 담당합니다.
    """

    def __init__(self, customer_selector):
        self._customer_selector = customer_selector

    def generate_token(self, user: User) -> Tuple[str, str]:
        """
        이 함수는 유저로 refresh_token과 access_token을 생성합니다.

        Args:
            user: 유저 객체

        Returns:
            Tuple[str, str]: refresh_token, access_token
        """
        refresh_token = RefreshToken.for_user(user)
        return str(refresh_token), str(refresh_token.access_token)

    def authenticate_user(self, user: User) -> User:
        """
        이 함수는 유저의 활성화 상태를 검증하고,
            마지막 로그인 시간 및 삭제 상태를 업데이트합니다.

        Args:
            user: 유저 객체

        Returns:
            User: 유저 객체
        """
        if user.is_active is False:
            raise AuthenticationFailedException("User is inactive")

        if user.is_deleted is True and user.deleted_at is not None:
            user.is_deleted = False
            user.deleted_at = None

        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "is_deleted", "deleted_at"])

        return user

    def update_token_with_pet_kindergarden_id(self, user, pet_kindergarden_id: int) -> Tuple[str, str]:
        """
        이 함수는 반려동물 유치원 아이디를 JWT Token Claim에 추가하는 함수입니다.

        Args:
            user: 유저 객체
            pet_kindergarden_id (int): 반려동물 유치원 아이디

        Returns:
            Tuple[str, str]: refresh_token, access_token
        """
        check_object_or_not_found(
            self._customer_selector.exists_by_user_and_pet_kindergarden_id(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )
        refresh_token = RefreshToken.for_user(user)
        refresh_token["pet_kindergarden_id"] = pet_kindergarden_id
        return str(refresh_token), str(refresh_token.access_token)
