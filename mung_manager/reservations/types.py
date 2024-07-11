from datetime import datetime
from typing import TypedDict

attendance_type = TypedDict(
    "attendance_type",
    {
        "reservation_id": int,
        "ticket_type": str,
        "created_at": datetime,
        "reserved_at": datetime,
        "customer_pet_name": str,
        "is_attended": bool,
        "reservation_change_option": str,
        "usage_time": int | None,
        "used_ticket_count": str | None,
        "attendance_status": str,
        "price": int,
    },
)

is_expired_type = TypedDict(
    "is_expired_type",
    {
        "is_expired": bool,
    },
)
