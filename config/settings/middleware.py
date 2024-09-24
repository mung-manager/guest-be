from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpRequest
from django.http import HttpResponse
from typing import Callable
from mung_manager.pet_kindergardens.containers import PetKindergardenContainer
from mung_manager_commons.constants import SYSTEM_CODE
from mung_manager_commons.errors import NotFoundException
from mung_manager_db.models import PetKindergarden


class CustomJWTAuthorizationMiddleware(MiddlewareMixin):
    """
    이 클래스는 JWT 토큰에서 반려동물 유치원 아이디를 검증 후 객체를 주입합니다.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse] | None = ...) -> None:
        super().__init__(get_response)
        self._pet_kindergarden_selector = PetKindergardenContainer.pet_kindergarden_selector()

    def validate_pet_kindergarden(self, pet_kindergarden_id: int, user_id: int) -> PetKindergarden:
        pet_kindergarden = self._pet_kindergarden_selector.get_by_id_and_user_id(
            pet_kindergarden_id=pet_kindergarden_id, user_id=user_id
        )
        if pet_kindergarden is None:
            raise NotFoundException(
                detail=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
                code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
            )
        return pet_kindergarden

    def process_request(self, request: HttpRequest):
        auth_header = request.META.get("HTTP_AUTHORIZATION", None)
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                validated_token = JWTAuthentication().get_validated_token(token)
                if validated_token.get("pet_kindergarden_id") is not None:
                    request.pet_kindergarden = self.validate_pet_kindergarden(
                        pet_kindergarden_id=validated_token.get("pet_kindergarden_id"),
                        user_id=validated_token.get("user_id"),
                    )
            except Exception:
                request.pet_kindergarden = None
        else:
            request.pet_kindergarden = None
