from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from mung_manager.authentications.containers import AuthenticationContainer
from mung_manager_db.enum_types import AuthGroup


class IsGuestPermission(permissions.BasePermission):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_selector = AuthenticationContainer.user_selector()

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        이 함수는 기본적으로 게스트 API에 적용되며, 유저의 권한이 게스트인지 확인합니다.

        Args:
            request (Request): Request 객체
            view (APIView): APIView 객체

        Returns:
            bool: 유저의 권한이 게스트이면 True, 아니면 False를 반환
        """
        try:
            if self._user_selector.exists_by_user_id_and_group_id_for_permission(
                user_id=request.user.id, group_id=AuthGroup.GUEST.value
            ):
                return True

            return False

        except Exception:
            return False
