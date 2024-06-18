from enum import Enum


class ReservationAvailabilityOption(Enum):
    """
    예약 가능 설정
    """

    SAME_DAY_AVAILABILITY = "당일 예약 가능"
    SAME_DAY_UNAVAILABILITY = "당일 예약 불가"


class ReservationChangeOption(Enum):
    """
    예약 변경 설정
    """

    SAME_DAY_CHANGE = "당일 변경 가능"
    SAME_DAY_UNCHANGE = "당일 변경 불가"
