from drf_spectacular.utils import OpenApiExample

ErrorTicketNotFoundSchema = OpenApiExample(
    name="404(ticket_not_found)",
    summary="[Not Found]: Ticket Not Found",
    description="""
    해당 반려동물 유치원 티켓을 찾을 수 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 404,
        "code": "not_found_ticket",
        "message": "Ticket does not exist.",
        "data": {},
    },
    status_codes=["404"],
    response_only=True,
)
