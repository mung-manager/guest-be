from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from mung_manager.authentications.enums import AuthGroup
from mung_manager.customers.containers import CustomerContainer


class IsGuestPermission(permissions.BasePermission):
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
            if request.user.groups.first().id == AuthGroup.GUEST.value:  # type: ignore
                return True

            return False

        except Exception:
            return False


class PetKindergardenAccessPermission(permissions.BasePermission):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._customer_selector = CustomerContainer.customer_selector()

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        이 함수는 기본적으로 게스트 API에 적용되며, 유저가 반려동물 유치원에 속해 있는지 확인합니다.

        Args:
            request (Request): Request 객체
            view (APIView): APIView 객체

        Returns:
            bool: 반려동물 유치원에 속해 있으면 True, 아니면 False를 반환
        """
        try:
            if not request.user.is_authenticated:
                return False

            if self._customer_selector.exists_by_user_and_pet_kindergarden_id(
                user=request.user, pet_kindergarden_id=request.pet_kindergarden_id
            ):
                return True

            return False

        except Exception:
            return False
