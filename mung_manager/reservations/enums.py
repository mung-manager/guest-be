from enum import Enum


class ReservationStatus(Enum):
    """예약 상태"""

    COMPLETED = "완료"
    CANCELED = "취소"
    MODIFIED = "변경"
