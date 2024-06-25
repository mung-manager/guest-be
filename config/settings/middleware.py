from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpRequest


class CustomJWTAuthorizationMiddleware(MiddlewareMixin):
    """
    이 클래스는 JWT 토큰에서 반려동물 유치원 아이디를 검출합니다.
    """

    def process_request(self, request: HttpRequest):
        auth_header = request.META.get("HTTP_AUTHORIZATION", None)
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                validated_token = JWTAuthentication().get_validated_token(token)
                request.pet_kindergarden_id = validated_token.get("pet_kindergarden_id", None)
            except Exception:
                request.pet_kindergarden_id = None
        else:
            request.pet_kindergarden_id = None
