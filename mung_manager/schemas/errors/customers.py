from drf_spectacular.utils import OpenApiExample

ErrorCustomerPermissionDeniedSchema = OpenApiExample(
    name="403(inactive_customer)",
    summary="[Permission Denied]: Inactive Customer",
    description="""
    해당 고객이 비활성화 상태일 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 403,
        "code": "inactive_customer",
        "message": "Customer is inactive.",
        "data": {},
    },
    status_codes=["403"],
    response_only=True,
)

ErrorCustomerNotFoundSchema = OpenApiExample(
    name="404(customer_not_found)",
    summary="[Not Found]: Customer Not Found",
    description="""
    해당 고객을 찾을 수 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 404,
        "code": "not_found_customer",
        "message": "Customer does not exist.",
        "data": {},
    },
    status_codes=["404"],
    response_only=True,
)

ErrorCustomerPetNotFoundSchema = OpenApiExample(
    name="404(customer_pet_not_found)",
    summary="[Validation Failed]: Customer Pet Not Found",
    description="""
    고객의 반려동물을 찾을 수 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 404,
        "code": "customer_pet_not_found",
        "message": "Customer pet does not exist.",
        "data": {},
    },
    status_codes=["404"],
    response_only=True,
)

ErrorCustomerTicketConflictSchema = OpenApiExample(
    name="409(conflict_ticket)",
    summary="[Conflict]: Conflict Ticket",
    description="""
    예약 등록에 실패했을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 409,
        "code": "conflict_customer_ticket",
        "message": "Reservation failed to register, please try again.",
        "data": {},
    },
    status_codes=["409"],
    response_only=True,
)
