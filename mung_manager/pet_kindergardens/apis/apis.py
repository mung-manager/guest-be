from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthMixin, APIAuthWithPetKindergardenAccessMixin
from mung_manager.authentications.containers import AuthenticationContainer
from mung_manager.commons.base.serializers import BaseSerializer
from mung_manager.pet_kindergardens.containers import PetKindergardenContainer


class PetKindergardenListAPI(APIAuthMixin, APIView):

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(label="유치원 아이디")
        name = serializers.CharField(label="유치원 이름")
        profile_thumbnail_url = serializers.CharField(label="프로필 URL")
        full_address = serializers.CharField(label="전체 주소")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pet_kindergarden_selector = PetKindergardenContainer.pet_kindergarden_selector()

    def get(self, request: Request) -> Response:
        pet_kindergardens = self._pet_kindergarden_selector.get_queryset_by_user(user=request.user)
        pet_kindergardens_data = self.OutputSerializer(pet_kindergardens, many=True).data
        return Response(data=pet_kindergardens_data, status=status.HTTP_200_OK)


class PetKindergardenSelectionAPI(APIAuthMixin, APIView):

    class InputSerializer(BaseSerializer):
        pet_kindergarden_id = serializers.IntegerField(label="유치원 id")

    class OutputSerializer(BaseSerializer):
        access_token = serializers.CharField(label="액세스 토큰")
        refresh_token = serializers.CharField(label="리프레쉬 토큰")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auth_service = AuthenticationContainer.auth_service()
        self._pet_kindergarden_service = PetKindergardenContainer.pet_kindergarden_service()

    def post(self, request: Request) -> Response:
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user = request.user
        pet_kindergarden_id = input_serializer.validated_data["pet_kindergarden_id"]
        refresh_token, access_token = self._auth_service.update_token_with_pet_kindergarden_id(
            user, pet_kindergarden_id
        )
        auth_data = self.OutputSerializer(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ).data
        return Response(data=auth_data, status=status.HTTP_200_OK)


class PetKindergardenSummaryInfoAPI(APIAuthWithPetKindergardenAccessMixin, APIView):
    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(label="유치원 아이디")
        name = serializers.CharField(label="유치원 이름")
        business_hour = serializers.CharField(label="유치원 영업 시간")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pet_kindergarden_selector = PetKindergardenContainer.pet_kindergarden_selector()

    def get(self, request: Request) -> Response:
        pet_kindergarden_id = request.pet_kindergarden_id
        pet_kindergarden = self._pet_kindergarden_selector.get_by_pet_kindergarden_id_for_summary_info(
            pet_kindergarden_id
        )
        summary_info_data = {
            "id": pet_kindergarden["id"],
            "name": pet_kindergarden["name"],
            "business_hour": pet_kindergarden["business_start_hour"].strftime("%H:%M")
            + " - "
            + pet_kindergarden["business_end_hour"].strftime("%H:%M"),
        }
        pet_kindergardens_data = self.OutputSerializer(summary_info_data).data
        return Response(data=pet_kindergardens_data, status=status.HTTP_200_OK)
