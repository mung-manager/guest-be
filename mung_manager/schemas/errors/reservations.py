from drf_spectacular.utils import OpenApiExample

ErrorReservationNotFoundSchema = OpenApiExample(
    name="404(reservation_not_found)",
    summary="[Not Found]: Reservation Not Found",
    description="""
    해당 예약을 찾을 수 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 404,
        "code": "not_found_reservation",
        "message": "Reservation does not exist.",
        "data": {},
    },
    status_codes=["404"],
    response_only=True,
)