from enum import Enum


class TicketType(Enum):
    """티켓 타입"""

    TIME = "시간"
    ALL_DAY = "종일"
    HOTEL = "호텔"
