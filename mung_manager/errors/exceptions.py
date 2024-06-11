from rest_framework import status

from mung_manager.common.base.exceptions import BaseAPIException
from mung_manager.common.constants import SYSTEM_CODE


class InvalidParameterFormatException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = SYSTEM_CODE.message("INVALID_PARAMETER_FORMAT")
    default_code = SYSTEM_CODE.code("INVALID_PARAMETER_FORMAT")


class ValidationException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = SYSTEM_CODE.message("VALIDATION_FAILED")
    default_code = SYSTEM_CODE.code("VALIDATION_FAILED")


class AlreadyExistsException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = SYSTEM_CODE.message("ALREADY_EXISTS")
    default_code = SYSTEM_CODE.code("ALREADY_EXISTS")


class InvalidTokenException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = SYSTEM_CODE.message("INVALID_TOKEN")
    default_code = SYSTEM_CODE.code("INVALID_TOKEN")


class AuthenticationFailedException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = SYSTEM_CODE.message("AUTHENTICATION_FAILED")
    default_code = SYSTEM_CODE.code("AUTHENTICATION_FAILED")


class PermissionDeniedException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = SYSTEM_CODE.message("PERMISSION_DENIED")
    default_code = SYSTEM_CODE.code("PERMISSION_DENIED")


class NotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = SYSTEM_CODE.message("NOT_FOUND")
    default_code = SYSTEM_CODE.code("NOT_FOUND")


class UnknownServerException(BaseAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = SYSTEM_CODE.message("UNKNOWN_SERVER_ERROR")
    default_code = SYSTEM_CODE.code("UNKNOWN_SERVER_ERROR")


class NotImplementedException(BaseAPIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = SYSTEM_CODE.message("NOT_IMPLEMENTED")
    default_code = SYSTEM_CODE.code("NOT_IMPLEMENTED")
