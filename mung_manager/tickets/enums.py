from enum import Enum


class TicketType(Enum):
    """
    티켓 타입
    """

    TIME = "시간"
    ALL_DAY = "종일"
    HOTEL = "호텔"


class TicketStatus(Enum):
    """
    티켓 상태
    """

    PENDING = "등원 예정"
    COMPLETED = "이용 완료"
