from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mung_manager.apis.mixins import APIAuthMixin
from mung_manager.authentications.containers import AuthenticationContainer
from mung_manager.commons.base.serializers import BaseSerializer
from mung_manager.commons.utils import inline_serializer
from mung_manager.pet_kindergardens.containers import PetKindergardenContainer
from mung_manager.tickets.containers import TicketContainer


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


class PetKindergardenSummaryInfoAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(label="유치원 아이디")
        name = serializers.CharField(label="유치원 이름")
        business_start_hour = serializers.TimeField(label="영업 시작 시간", format="%H:%M")
        business_end_hour = serializers.TimeField(label="영업 종료 시간", format="%H:%M")

    def get(self, request: Request) -> Response:
        pet_kindergardens_data = self.OutputSerializer(request.pet_kindergarden).data
        return Response(data=pet_kindergardens_data, status=status.HTTP_200_OK)


class PetKindergardenDetailInfoAPI(APIAuthMixin, APIView):
    class OutputSerializer(BaseSerializer):
        name = serializers.CharField(label="반려동물 유치원 이름")
        profile_thumbnail_url = serializers.URLField(label="프로필 이미지 URL")
        visible_phone_number = serializers.ListField(child=serializers.CharField(), label="노출 전화번호")
        business_start_hour = serializers.TimeField(label="영업 시작 시간", format="%H:%M")
        business_end_hour = serializers.TimeField(label="영업 종료 시간", format="%H:%M")
        road_address = serializers.CharField(label="도로명 주소")
        abbr_address = serializers.CharField(label="지번 주소")
        detail_address = serializers.CharField(label="상세 주소")
        guide_message = serializers.CharField(label="안내 메시지")
        reservation_availability_option = serializers.CharField(label="예약 가능 설정")
        reservation_change_option = serializers.CharField(label="예약 변경 옵션")
        tickets = inline_serializer(
            many=True,
            fields={
                "ticket_type": serializers.CharField(label="티켓 타입"),
                "usage_time": serializers.IntegerField(label="사용 가능한 시간"),
                "usage_count": serializers.IntegerField(label="사용 가능한 횟수"),
                "usage_period_in_days_count": serializers.IntegerField(label="사용 기간(일) 횟수"),
                "price": serializers.IntegerField(label="금액"),
            },
            label="티켓",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ticket_selector = TicketContainer.ticket_selector()

    def get(self, request: Request) -> Response:
        pet_kindergarden = request.pet_kindergarden
        tickets = self._ticket_selector.get_querset_by_pet_kindergarden_id_for_undeleted_ticket(pet_kindergarden.id)
        pet_kindergarden_data = {
            "name": pet_kindergarden.name,
            "profile_thumbnail_url": pet_kindergarden.profile_thumbnail_url,
            "visible_phone_number": pet_kindergarden.visible_phone_number,
            "business_start_hour": pet_kindergarden.business_start_hour,
            "business_end_hour": pet_kindergarden.business_end_hour,
            "road_address": pet_kindergarden.road_address,
            "abbr_address": pet_kindergarden.abbr_address,
            "detail_address": pet_kindergarden.detail_address,
            "guide_message": pet_kindergarden.guide_message,
            "reservation_availability_option": pet_kindergarden.reservation_availability_option,
            "reservation_change_option": pet_kindergarden.reservation_change_option,
            "tickets": tickets,
        }
        data = self.OutputSerializer(pet_kindergarden_data).data
        return Response(data=data, status=status.HTTP_200_OK)
