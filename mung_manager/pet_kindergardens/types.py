from datetime import time
from typing import TypedDict

info_for_full_address = TypedDict("info_for_full_address", {"full_address": str})
info_for_summary = TypedDict(
    "info_for_summary", {"id": int, "name": str, "business_start_hour": time, "business_end_hour": time}
)
