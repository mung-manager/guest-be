from drf_spectacular.utils import OpenApiExample

ErrorInvalidParameterFormatSchema = OpenApiExample(
    name="400(invalid_parameter_format)",
    summary="[Default Invalid Parameter Format]",
    description="""
    요청 파라미터의 형식이 올바르지 않을 때 반환되는 응답입니다.
    message 필드에는 발생한 오류에 대해 딕셔너리 형태로 설명이 포함됩니다.
    예를 들어 필수 파라미터가 누락되었을 경우 다음과 같이 반환됩니다.
    {
        "message": {
            "example_field": "This field is required."
        }
    }
    """,
    value={
        "success": False,
        "statusCode": 400,
        "code": "invalid_parameter_format",
        "message": "The parameter format is incorrect.",
        "data": {},
    },
    status_codes=["400"],
    response_only=True,
)

ErrorValidationFailedSchema = OpenApiExample(
    name="400(validation_failed)",
    summary="[Default Validation Failed]",
    description="""
    데이터 유효성 검사에 실패했을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 400,
        "code": "validation_failed",
        "message": "Validation failed.",
        "data": {},
    },
    status_codes=["400"],
    response_only=True,
)

ErrorAlreadyExistsSchema = OpenApiExample(
    name="400(already_exists)",
    summary="[Default Already Exists]",
    description="""
    해당 객체가 이미 존재할 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 400,
        "code": "already_exists",
        "message": "This object already exists.",
        "data": {},
    },
    status_codes=["400"],
    response_only=True,
)

ErrorAuthenticationFailedSchema = OpenApiExample(
    name="401(authentication_failed)",
    summary="[Default Authentication Failed]",
    description="""
    인증에 실패했을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "Incorrect authentication credentials.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorNotAuthenticatedSchema = OpenApiExample(
    name="401(not_authenticated)",
    summary="[Default Not Authenticated]",
    description="""
    인증되지 않은 사용자가 요청을 보냈을 때 반환되는 응답입니다.
    Header Authorization에 Bearer Token을 포함시켜주세요.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "not_authenticated",
        "message": "Authentication credentials were not provided.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorInvalidTokenSchema = OpenApiExample(
    name="401(invalid_token)",
    summary="[Default Invalid Token]",
    description="""
    토큰이 유효하지 않거나 만료되었을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "token_not_valid",
        "message": "Token is invalid or expired",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)


ErrorPermissionDeniedSchema = OpenApiExample(
    name="403(permission_denied)",
    summary="[Default Permission Denied]",
    description="""
    해당 요청에 대한 권한이 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 403,
        "code": "permission_denied",
        "message": "You do not have permission to perform this action.",
        "data": {},
    },
    status_codes=["403"],
    response_only=True,
)

ErrorNotFoundSchema = OpenApiExample(
    name="404(not_found)",
    summary="[Default Not Found]",
    description="""
    해당 리소스를 찾을 수 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 404,
        "code": "not_found",
        "message": "Not found.",
        "data": {},
    },
    status_codes=["404"],
    response_only=True,
)

ErrorUnknownServerSchema = OpenApiExample(
    name="500(unknown_server_error)",
    summary="[Default Unknown Server Error]",
    description="""
    서버가 알 수 없는 오류가 발생했을 때 반환되는 응답입니다.
    서버 개발자에게 문의해주세요.
    """,
    value={
        "success": False,
        "statusCode": 500,
        "code": "unknown_server_error",
        "message": "An unknown server error occurred.",
        "data": {},
    },
    status_codes=["500"],
    response_only=True,
)

ErrorNotImplementedSchema = OpenApiExample(
    name="501(not_implemented)",
    summary="[Default Not Implemented]",
    description="""
    해당 기능이 구현되지 않았을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 501,
        "code": "not_implemented",
        "message": "This feature is not implemented yet.",
        "data": {},
    },
    status_codes=["501"],
    response_only=True,
)

ErrorPhoneNumberInvalidSchema = OpenApiExample(
    name="400(phone_number_invalid)",
    summary="[Validation Failed]: Phone Number Invalid",
    description="""
    전화번호가 올바르지 않을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 400,
        "code": "validation_failed",
        "message": "Enter a valid phone number (e.g. 010-0000-0000).",
        "data": {},
    },
    status_codes=["400"],
    response_only=True,
)
