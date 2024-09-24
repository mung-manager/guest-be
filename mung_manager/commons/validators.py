from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager_db.enum_types import TicketType


class InvalidPhoneNumberValidator(RegexValidator):
    """
    이 클래스는 전화번호의 유효성을 검사합니다.

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
    """
    이 클래스는 반려동물 이름의 중복을 검사합니다.

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
    """
    이 클래스는 예약 가능 시간을 검사합니다.

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
    """
    이 클래스는 종료 시간을 검사합니다.

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


class InvalidTicketTypeValidator:
    """
    이 클래스는 티켓 타입을 검사합니다.

    Attributes:
        message: 티켓 타입 유효성 검사 실패시 반환 메시지
        code: 티켓 타입 유효성 검사 실패시 반환 코드
    """

    message = SYSTEM_CODE.message("INVALID_TICKET_TYPE")
    code = SYSTEM_CODE.code("INVALID_TICKET_TYPE")

    def __call__(self, value):
        if value.endswith(TicketType.TIME.value):
            time_value = value[:-2]
            if not time_value.isdigit() or int(time_value) <= 0:
                raise ValidationError(message=self.message, code=self.code)
        elif value not in [item.value for item in TicketType]:
            raise ValidationError(message=self.message, code=self.code)


class AvailableDatesAPIParameterValidator:
    """
    이 클래스는 예약 가능한 날짜 조회 기능에서의 파라미터를 검사합니다.

    Attributes:
        message: 파라미터 유효성 검사 실패시 반환 메시지
        code: 파라미터 유효성 검사 실패시 반환 코드
    """

    message = SYSTEM_CODE.message("INVALID_PARAMETER_FORMAT")
    code = SYSTEM_CODE.code("INVALID_PARAMETER_FORMAT")

    def __call__(self, attrs):
        ticket_type = attrs.get("ticket_type")
        ticket_id = attrs.get("ticket_id")

        if ticket_type == TicketType.HOTEL.value:
            if ticket_id is not None:
                raise ValidationError(message=self.message, code=self.code)
        elif ticket_id is None:
            raise ValidationError(message=self.message, code=self.code)


class CreateReservationAPIParameterValidator:
    """
    이 클래스는 예약하기 기능에서의 파라미터를 검사합니다.

    Attributes:
        message: 파라미터 유효성 검사 실패시 반환 메시지
        code: 파라미터 유효성 검사 실패시 반환 코드
    """

    message = SYSTEM_CODE.message("INVALID_PARAMETER_FORMAT")
    code = SYSTEM_CODE.code("INVALID_PARAMETER_FORMAT")

    def __call__(self, attrs):
        required_fields = {
            TicketType.TIME.value: ["pet_id", "ticket_type", "ticket_id", "reserved_date", "attendance_time"],
            TicketType.ALL_DAY.value: ["pet_id", "ticket_type", "ticket_id", "reserved_date"],
            TicketType.HOTEL.value: ["pet_id", "ticket_type", "reserved_date", "end_date"],
        }

        ticket_type = attrs.get("ticket_type")[-2:]

        if ticket_type not in required_fields:
            raise ValidationError(message=self.message, code=self.code)

        for field in required_fields[ticket_type]:
            if field not in attrs or not attrs[field]:
                raise ValidationError(message=self.message, code=self.code)
