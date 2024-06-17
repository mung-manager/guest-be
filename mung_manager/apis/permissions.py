from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from mung_manager.authentication.enums import AuthGroup


class IsGuestPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView):
        """이 함수는 기본적으로 게스트 API에 적용되며, 유저의 권한이 게스트인지 확인합니다.

        Args:
            request (Request): Request 객체
            view (APIView): APIView 객체

        Returns:
            bool: 유저의 권한이 게스트이면 True, 아니면 False를 반환
        """
        try:
            if request.user.groups.first().id == AuthGroup.GUEST.value:  # type: ignore
                return True

            return False

        except Exception:
            return False
