from datetime import datetime

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.authentications.containers import AuthenticationContainer
from mung_manager.authentications.enums import UserProvider
from mung_manager.common.base.serializers import BaseSerializer
from mung_manager.errors.exceptions import AuthenticationFailedException


class KakaoLoginAPI(APIView):
    class InputSerializer(BaseSerializer):
        code = serializers.CharField(required=True, help_text="카카오 인증 코드")
        error = serializers.CharField(required=False, help_text="카카오 에러 코드")
        redirect_uri = serializers.CharField(required=True, help_text="리다이렉트 URI")

    class OutputSerializer(BaseSerializer):
        access_token = serializers.CharField(label="액세스 토큰")
        refresh_token = serializers.CharField(label="리프레쉬 토큰")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auth_service = AuthenticationContainer.auth_service()
        self._kakao_login_flow_service = AuthenticationContainer.kakao_login_flow_service()
        self._user_service = AuthenticationContainer.user_service()

    def get(self, request: Request) -> Response:
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data
        code = validated_data.get("code")
        error = validated_data.get("error")
        redirect_uri = validated_data.get("redirect_uri")

        if error is not None:
            raise AuthenticationFailedException(error)

        # 카카오 로그인 플로우
        kakao_token = self._kakao_login_flow_service.get_token(code=code, redirect_uri=redirect_uri)
        user_info = self._kakao_login_flow_service.get_user_info(kakao_token=kakao_token)

        # 유저 정보 추출
        social_id = user_info["id"]
        email = user_info["kakao_account"]["email"]
        name = user_info["kakao_account"]["name"]
        phone_number = user_info["kakao_account"].get("phone_number")
        birthyear = user_info["kakao_account"].get("birthyear")
        birthday = user_info["kakao_account"].get("birthday")
        gender = user_info["kakao_account"].get("gender")
        has_phone_number = user_info["kakao_account"].get("has_phone_number")

        phone_number = phone_number.replace("+82 ", "0")
        birth = datetime.strptime(birthyear + birthday, "%Y%m%d") if birthyear and birthday else ""
        gender = "F" if gender == "female" else "M" if gender == "male" else ""

        # 소셜 유저 생성
        user = self._user_service.create_kakao_user(
            social_id=social_id,
            name=name,
            email=email,
            phone_number=phone_number,
            birth=birth,
            gender=gender,
            social_provider=UserProvider.KAKAO.value,
            has_phone_number=has_phone_number,
        )

        # 유저 토큰 발급
        self._auth_service.authenticate_user(user)
        refresh_token, access_token = self._auth_service.generate_token(user)
        auth_data = self.OutputSerializer(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ).data
        return Response(data=auth_data, status=status.HTTP_200_OK)
