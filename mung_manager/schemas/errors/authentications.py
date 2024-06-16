from drf_spectacular.utils import OpenApiExample

ErrorAuthorizationHeaderSchema = OpenApiExample(
    name="401(bad_authorization_header)",
    summary="[Authentication Failed]: Bad Authorization Header",
    description="""
    Authorization header에 두 개의 공백으로 구분된 값이 포함되어 있지 않을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": {
            "detail": "Authorization header must contain two space-delimited values",
            "code": "bad_authorization_header",
        },
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorTokenIdentificationSchema = OpenApiExample(
    name="401(token_identification_failed)",
    summary="[Authentication Failed]: Token Identification Failed",
    description="""
    토큰에 유저 식별 정보가 포함되어 있지 않을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "token_not_valid",
        "message": "Token contained no recognizable user identification.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorAuthenticationUserNotFoundSchema = OpenApiExample(
    name="401(user_not_found)",
    summary="[Authentication Failed]: User Not Found",
    description="""
    토큰에 포함된 유저 식별 정보로 유저를 찾을 수 없을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "User not found",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorAuthenticationUserInactiveSchema = OpenApiExample(
    name="401(user_inactive)",
    summary="[Authentication Failed]: User Inactive",
    description="""
    유저가 비활성화 상태일 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "User is inactive",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorAuthenticationPasswordChangedSchema = OpenApiExample(
    name="401(password_changed)",
    summary="[Authentication Failed]: Password Changed",
    description="""
    토큰에 포함된 유저의 비밀번호가 변경되었을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "The user's password has been changed.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorAuthenticationUserDeletedSchema = OpenApiExample(
    name="401(user_deleted)",
    summary="[Authentication Failed]: User Deleted",
    description="""
    유저가 삭제된 상태일 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "User is deleted",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorOauthErrorSchema = OpenApiExample(
    name="401(oauth_error)",
    summary="[Authentication Failed]: OAuth Error",
    description="""
    OAuth 인증 과정에서 발생한 에러일 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "{error}",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorKakaoAccessTokenFailedSchema = OpenApiExample(
    name="401(kakao_access_token_failed)",
    summary="[Authentication Failed]: Kakao Access Token Failed",
    description="""
    카카오 토큰을 얻는 과정에서 실패했을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "Failed to get access token from Kakao.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorKakaoUserInfoFailedSchema = OpenApiExample(
    name="401(kakao_user_info_failed)",
    summary="[Authentication Failed]: Kakao User Info Failed",
    description="""
    카카오 유저 정보를 얻는 과정에서 실패했을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "Failed to get user info from Kakao.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorKakaoPhoneNumberNotAuthenticatedSchema = OpenApiExample(
    name="401(kakao_phone_number_not_authenticated)",
    summary="[Authentication Failed]: Kakao Phone Number Not Authenticated",
    description="""
    카카오 전화번호가 인증되지 않았을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "Kakao phone number is not authenticated.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)

ErrorKakaoLocationFailedSchema = OpenApiExample(
    name="401(kakao_location_failed)",
    summary="[Authentication Failed]: Kakao Location Failed",
    description="""
    카카오 위치 정보를 얻는 과정에서 실패했을 때 반환되는 응답입니다.
    """,
    value={
        "success": False,
        "statusCode": 401,
        "code": "authentication_failed",
        "message": "Failed to get coordinates from Kakao.",
        "data": {},
    },
    status_codes=["401"],
    response_only=True,
)
