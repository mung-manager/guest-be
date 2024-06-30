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
