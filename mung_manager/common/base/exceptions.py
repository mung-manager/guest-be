from rest_framework import status
from rest_framework.exceptions import APIException

from mung_manager.common.constants import SYSTEM_CODE


class BaseAPIException(APIException):
    """기본 API 예외 클래스입니다.
        이 클래스는 프로젝트에서 사용되는 모든 API 예외 클래스의 기본 형태를 정의합니다.

    Attributes:
        status_code (int): 예외에 대한 HTTP 상태 코드
        default_detail (str): 예외에 대한 기본 상세 설명
        code (str): 예외 코드입니다. 대문자로 작성되어야 함
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail: str = SYSTEM_CODE.message("BAD_REQUEST")
    default_code: str = SYSTEM_CODE.code("BAD_REQUEST")
