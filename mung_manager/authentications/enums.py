from enum import Enum


class UserProvider(Enum):
    """유저 로그인 제공자"""

    EMAIL = 1
    KAKAO = 2


class AuthGroup(Enum):
    """인증 그룹"""

    ADMIN = 1
    SUPERUSER = 2
    GUEST = 3
    PARTNER = 4
