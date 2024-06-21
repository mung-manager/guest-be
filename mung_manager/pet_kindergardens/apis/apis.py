from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthMixin
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
