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
