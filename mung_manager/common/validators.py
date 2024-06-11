from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

from mung_manager.common.constants import SYSTEM_CODE


class InvalidPhoneNumberValidator(RegexValidator):
    """이 클래스는 전화번호의 유효성을 검사합니다.

    Attributes:
        regex: 전화번호 정규식
        message: 전화번호 유효성 검사 실패시 반환 메시지
    """

    regex = r"^010-\d{4}-\d{4}$"
    message = SYSTEM_CODE.message("INVALID_PHONE_NUMBER")

    def __call__(self, value):
        try:
            super().__call__(value)
        except ValidationError:
            raise ValidationError(self.message, code=self.code)


class UniquePetNameValidator:
    """이 클래스는 반려동물 이름의 중복을 검사합니다.

    Attributes:
        message: 반려동물 이름 중복시 반환 메시지
        code: 반려동물 이름 중복시 반환 코드
    """

    message = SYSTEM_CODE.message("UNIQUE_PET_NAME")
    code = SYSTEM_CODE.code("UNIQUE_PET_NAME")

    def __call__(self, value):
        if len(value) != len(set(value)):
            raise ValidationError(message=self.message, code=self.code)


class InvalidReservedAtValidator:
    """이 클래스는 예약 가능 시간을 검사합니다.

    Attributes:
        message: 예약 가능 시간 유효성 검사 실패시 반환 메시지
        code: 예약 가능 시간 유효성 검사 실패시 반환 코드
    """

    message = SYSTEM_CODE.message("INVALID_RESERVED_AT")
    code = SYSTEM_CODE.code("INVALID_RESERVED_AT")

    def __call__(self, value):
        if value <= timezone.now():
            raise ValidationError(message=self.message, code=self.code)


class InvalidEndAtValidator:
    """이 클래스는 종료 시간을 검사합니다.

    Attributes:
        message: 종료 시간 유효성 검사 실패시 반환 메시지
        code: 종료 시간 유효성 검사 실패시 반환 코드
    """

    requires_context = True
    message = SYSTEM_CODE.message("INVALID_END_AT")
    code = SYSTEM_CODE.code("INVALID_END_AT")

    def __call__(self, value, serializer_field):
        reserved_at = serializer_field.parent.initial_data.get("reserved_at")
        if reserved_at:
            reserved_at = datetime.fromisoformat(reserved_at)
            if value <= reserved_at:
                raise ValidationError(message=self.message, code=self.code)
