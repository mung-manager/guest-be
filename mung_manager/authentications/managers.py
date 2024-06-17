from django.contrib.auth.models import BaseUserManager

from mung_manager.authentications.enums import AuthGroup, UserProvider


class UserManager(BaseUserManager):
    def create_kakao_user(self, email: str, social_id: str, social_provider: int, **extra_fields):
        """이 함수는 유저 데이터를 받아 소셜 유저를 생성 후 그룹(파트너)을 추가합니다.

        Args:
            email (str): 이메일
            social_id (str): 소셜 아이디
            social_provider (int): 소셜 제공자
            **extra_fields: 추가적인 필드

        Returns:
            User: 유저 객체
        """
        email = self.normalize_email(email)
        user = self.model(
            social_id=social_id,
            email=email,
            user_social_provider_id=social_provider,
            **extra_fields,
        )
        # @TODO: Fixed Type
        user.set_unusable_password()  # type: ignore
        user.save(using=self._db)

        user.groups.add(AuthGroup.GUEST.value)  # type: ignore
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        """이 함수는 유저 데이터를 받아 슈퍼유저를 생성 후 그룹(슈퍼유저)을 추가합니다.

        Args:
            email (str): 이메일
            password (str): 비밀번호
            **extra_fields: 추가적인 필드

        Returns:
            User: 유저 객체
        """
        email = self.normalize_email(email)
        user = self.model(
            social_id="",
            email=email,
            is_superuser=True,
            is_admin=True,
            user_social_provider_id=UserProvider.EMAIL.value,
            **extra_fields,
        )
        # @TODO: Fixed Type
        user.set_password(password)  # type: ignore
        user.save(using=self._db)

        user.groups.add(AuthGroup.SUPERUSER.value)  # type: ignore
        return user

    def create_admin(self, email: str, password: str, **extra_fields):
        """이 함수는 유저 데이터를 받아 관리자를 생성 후 그룹(관리자)을 추가합니다.

        Args:
            email (str): 이메일
            password (str): 비밀번호
            **extra_fields: 추가적인 필드

        Returns:
            User: 유저 객체
        """
        email = self.normalize_email(email)
        user = self.model(
            social_id="",
            email=email,
            is_admin=True,
            user_social_provider_id=UserProvider.EMAIL.value,
            **extra_fields,
        )
        # @TODO: Fixed Type
        user.set_password(password)  # type: ignore
        user.save(using=self._db)

        user.groups.add(AuthGroup.ADMIN.value)  # type: ignore
        return user
