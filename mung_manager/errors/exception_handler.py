from datetime import datetime

from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from config.settings.logging import logger
from mung_manager.errors.exceptions import UnknownServerException, ValidationException


def default_exception_handler(exc: Exception, context: dict) -> Response:
    """기본 예외 처리 핸들러입니다.
        Django의 ValidationError의 예외 처리를 수행하고
        DRF의 기본 예외 처리를 오버라이딩하여 커스텀 예외 처리를 수행합니다.

    Args:
        exc (Exception): 발생한 예외 객체
        context (dict): 예외가 발생한 컨텍스트 정보

    Returns:
        Response: 예외 처리 결과로 생성된 Response 객체
    """
    # 로그 출력
    logger.error(f"[EXCEPTION_HANDLER]\n" f"[{datetime.now()}]\n" f"> exc\n" f"{exc}\n" f"> context\n" f"{context}")

    # 익셉션 핸들러를 통해 API 예외 처리를 시도
    # rest_framework에서 제공하는 APIException을 상속받은 예외를 처리하기 위해
    if isinstance(exc, APIException):
        response = handle_api_exception(exc=exc, context=context)

    # 익센션 핸들러를 통해 Django 유효성 검사 예외 처리를 시도
    # Django 데이터 유효성 검사에서 발생한 예외를 처리하기 위해
    if isinstance(exc, ValidationError):
        # @TODO: 슬랙 알림
        response = handle_django_validation_exception(exc=exc, context=context)

    # 익셉션 핸들러에서 처리가 완료되었다면 해당 Response를 반환
    if "response" in locals():
        return response

    # @TODO: 슬랙 알림
    return handle_api_exception(exc=UnknownServerException(), context=context)


def handle_api_exception(exc: APIException, context: dict) -> Response:
    """API 예외 처리를 수행하는 함수입니다.
        이 함수는 프로젝트 내에서 발생한 API 예외를 처리합니다.

    Args:
        exc (APIException): 발생한 예외 객체
        context (dict): 예외가 발생한 컨텍스트 정보

    Returns:
        Response: 예외 처리 결과로 생성된 Response 객체를 반환
    """
    message = getattr(exc, "detail")
    status_code = getattr(exc, "status_code")

    if hasattr(message, "code"):
        code = getattr(message, "code")
    else:
        code = getattr(exc, "default_code")

    return Response(data={"code": code, "message": message}, status=status_code)


def handle_django_validation_exception(exc: ValidationError, context: dict) -> Response:
    """Django의 유효성 검사 예외 처리를 수행하는 함수입니다.
        이 함수는 프로젝트 내에서 발생한 Django의 full_clean() 등의 유효성 검사 예외를 처리합니다.

    Args:
        exc (ValidationError): 발생한 예외 객체
        context (dict): 예외가 발생한 컨텍스트 정보

    Returns:
        Response: 예외 처리 결과로 생성된 Response 객체를 반환
    """
    status_code = getattr(ValidationException, "status_code")
    code = getattr(ValidationException, "default_code")

    if hasattr(exc, "message_dict"):
        message = getattr(exc, "message_dict")
    else:
        message = exc

    return Response(data={"code": code, "message": message}, status=status_code)
