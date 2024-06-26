from django.db import transaction

from mung_manager.authentications.enums import AuthGroup
from mung_manager.authentications.models import User
from mung_manager.authentications.selectors.users import UserSelector
from mung_manager.authentications.services.abstracts import AbstractUserService
from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.errors.exceptions import AuthenticationFailedException


class UserService(AbstractUserService):
    """이 클래스는 유저를 DB에 PUSH하는 비즈니스 로직을 담당합니다."""

    def __init__(self, user_selector: UserSelector):
        self._user_selector = user_selector

    @transaction.atomic
    def create_kakao_user(
        self,
        email: str,
        name: str,
        social_id: str,
        phone_number: str,
        birth: object,
        gender: str,
        social_provider: int,
        has_phone_number: bool,
    ) -> User:
        """이 함수는 유저 데이터를 받아 소셜 유저를 생성합니다.

        Args:
            email (str): 이메일
            name (str): 이름
            social_id (str): 소셜 아이디
            phone_number (str): 전화번호
            birth (object): 생년월일
            gender (str): 성별
            social_provider (int): 소셜 제공자
            has_phone_number (bool): 전화번호 인증 여부

        Returns:
            User: 유저 객체
        """
        # 전화번호 인증 여부 확인
        if has_phone_number is False:
            raise AuthenticationFailedException(
                detail=SYSTEM_CODE.message("NOT_AUTHENTICATED_KAKAO_PHONE_NUMBER"),
                code=SYSTEM_CODE.code("NOT_AUTHENTICATED_KAKAO_PHONE_NUMBER"),
            )

        user = self._user_selector.get_by_social_id(social_id)

        if user is not None:
            # 해당 유저가 파트너 그룹에 속하면서 게스트 그룹에 속하지 않을 때
            if self._user_selector.exists_by_user_id_and_group_id_for_group(
                user.id, AuthGroup.PARTNER.value, AuthGroup.GUEST.value
            ):
                user.groups.add(AuthGroup.GUEST.value)

            # 전화번호가 변경되었을 경우 업데이트
            if user.phone_number != phone_number:
                user.phone_number = phone_number
                user.save(update_fields=["phone_number"])

        if user is None:
            user = User.objects.create_kakao_user(
                email=email,
                name=name,
                phone_number=phone_number,
                social_id=social_id,
                social_provider=social_provider,
                birth=birth,
                gender=gender,
            )
        return user
