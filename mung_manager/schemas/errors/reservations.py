from drf_spectacular.utils import OpenApiExample

ErrorInvalidReservedAtSchema = OpenApiExample(
    name="400(validation_failed)",
    summary="[Validation Failed]",
    description="""
    예약 날짜가 유효하지 않을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 400,
        "code": "validation_failed",
        "message": "The reservation time is invalid.",
        "data": {},
    },
    status_codes=["400"],
    response_only=True,
)

ErrorInvalidEndAtSchema = OpenApiExample(
    name="400(validation_failed)",
    summary="[Validation Failed]",
    description="""
    하원 날짜가 유효하지 않을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 400,
        "code": "validation_failed",
        "message": "The reservation end time is invalid.",
        "data": {},
    },
    status_codes=["400"],
    response_only=True,
)


ErrorInvalidAttendanceTimeSchema = OpenApiExample(
    name="400(validation_failed)",
    summary="[Validation Failed]",
    description="""
    예약 시간이 유효하지 않을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 400,
        "code": "validation_failed",
        "message": "The attendance time is invalid.",
        "data": {},
    },
    status_codes=["400"],
    response_only=True,
)

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
