from math import floor
from typing import List, Tuple

import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import (
    check_object_or_already_exist,
    get_object_or_not_found,
)
from mung_manager.commons.services import update_model
from mung_manager.errors.exceptions import AuthenticationFailedException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.pet_kindergardens.services.abstracts import (
    AbstractPetKindergardenService,
)


class PetKindergardenService(AbstractPetKindergardenService):
    """이 클래스는 반려동물 유치원를 DB에 PUSH하는 비즈니스 로직을 담당합니다."""

    def __init__(self, pet_kindergarden_selector: PetKindergardenSelector):
        self._pet_kindergarden_selector = pet_kindergarden_selector

    def _get_coordinates_by_road_address(self, road_address: str) -> Tuple[float, float]:
        """이 함수는 도로명 주소를 받아 위도, 경도를 얻어옵니다.

        Args:
            road_address (str): 도로명 주소

        Returns:
            Tuple[float, float]: 위도, 경도
        """
        response = requests.get(
            url="https://dapi.kakao.com/v2/local/search/address.json",
            headers={"Authorization": f"KakaoAK {settings.KAKAO_API_KEY}"},
            # @TODO: Fixed Type
            params={  # type: ignore
                "analyze_type": "exact",
                "query": road_address,
                "page": 1,
                "size": 1,
            },
            timeout=3,
        )
        if response.status_code != 200:
            raise AuthenticationFailedException(
                detail=SYSTEM_CODE.message("AUTHENTICATION_FAILED_KAKAO_ADDRESS"),
                code=SYSTEM_CODE.code("AUTHENTICATION_FAILED_KAKAO_ADDRESS"),
            )

        response_data = response.json()

        latitude = floor(float(response_data["documents"][0]["road_address"]["y"]) * 10**6) / 10**6
        longitude = floor(float(response_data["documents"][0]["road_address"]["x"]) * 10**6) / 10**6

        return latitude, longitude

    @transaction.atomic
    def create_pet_kindergarden(
        self,
        user,
        name: str,
        profile_thumbnail_url: str,
        phone_number: str,
        visible_phone_number: List[str],
        business_start_hour: str,
        business_end_hour: str,
        road_address: str,
        abbr_address: str,
        detail_address: str,
        short_address: List[str],
        guide_message: str,
        reservation_availability_option: str,
        reservation_change_option: str,
        daily_pet_limit: int,
        main_thumbnail_url: str,
    ) -> PetKindergarden:
        """이 함수는 반려동물 유치원 데이터를 받아 반려동물 유치원을 생성합니다.

        Args:
            user (User): 유저 객체
            name (str): 반려동물 유치원 이름
            profile_thumbnail_url (str): 프로필 썸네일 URL
            phone_number (str): 전화번호
            visible_phone_number (List[str]): 보이는 전화번호
            business_start_hour (str): 영업 시작 시간
            business_end_hour (str): 영업 종료 시간
            road_address (str): 도로명 주소
            abbr_address (str): 간략 주소
            detail_address (str): 상세 주소
            short_address (list[str]): 짧은 주소
            guide_message (str): 가이드 메시지
            reservation_availability_option (str): 예약 가능 설정
            reservation_change_option (str): 예약 변경 옵션
            daily_pet_limit (int): 일일 반려동물 제한
            main_thumbnail_url (str): 메인 썸네일 URL

        Returns:
            PetKindergarden: 반려동물 유치원 객체
        """
        check_object_or_already_exist(
            self._pet_kindergarden_selector.exists_by_user(user),
            msg=SYSTEM_CODE.message("ALREADY_EXISTS_USER_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("ALREADY_EXISTS_USER_PET_KINDERGARDEN"),
        )
        # 도로명 주소로 위도, 경도를 조회
        latitude, longitude = self._get_coordinates_by_road_address(road_address)
        pet_kindergarden = PetKindergarden.objects.create(
            name=name,
            profile_thumbnail_url=profile_thumbnail_url,
            main_thumbnail_url=main_thumbnail_url,
            phone_number=phone_number,
            visible_phone_number=visible_phone_number,
            business_start_hour=business_start_hour,
            business_end_hour=business_end_hour,
            road_address=road_address,
            abbr_address=abbr_address,
            detail_address=detail_address,
            short_address=short_address,
            guide_message=guide_message,
            latitude=latitude,
            longitude=longitude,
            point=Point(longitude, latitude),
            reservation_availability_option=reservation_availability_option,
            reservation_change_option=reservation_change_option,
            daily_pet_limit=daily_pet_limit,
            user=user,
        )

        return pet_kindergarden

    @transaction.atomic
    def update_pet_kindergarden(
        self,
        user,
        pet_kindergarden_id: int,
        name: str,
        profile_thumbnail_url: str,
        phone_number: str,
        visible_phone_number: List[str],
        business_start_hour: str,
        business_end_hour: str,
        road_address: str,
        abbr_address: str,
        detail_address: str,
        short_address: List[str],
        guide_message: str,
        reservation_availability_option: str,
        reservation_change_option: str,
        daily_pet_limit: int,
        main_thumbnail_url: str,
    ) -> PetKindergarden:
        """이 함수는 반려동물 유치원 데이터를 받아 반려동물 유치원을 업데이트합니다.

        Args:
            user (User): 유저 객체
            name (str): 반려동물 유치원 이름
            profile_thumbnail_url (str): 프로필 썸네일 URL
            phone_number (str): 전화번호
            visible_phone_number (List[str]): 보이는 전화번호
            business_start_hour (str): 영업 시작 시간
            business_end_hour (str): 영업 종료 시간
            road_address (str): 도로명 주소
            abbr_address (str): 간략 주소
            detail_address (str): 상세 주소
            short_address (list[str]): 짧은 주소
            guide_message (str): 가이드 메시지
            reservation_availability_option (str): 예약 가능 설정
            reservation_change_option (str): 예약 변경 옵션
            daily_pet_limit (int): 일일 반려동물 제한
            main_thumbnail_url (str): 메인 썸네일 URL

        Returns:
            PetKindergarden: 반려동물 유치원 객체
        """
        pet_kindergarden = get_object_or_not_found(
            self._pet_kindergarden_selector.get_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )
        # 도로명 주소로 위도, 경도를 조회
        latitude, longitude = self._get_coordinates_by_road_address(road_address)

        data = {
            "name": name,
            "profile_thumbnail_url": profile_thumbnail_url,
            "main_thumbnail_url": main_thumbnail_url,
            "phone_number": phone_number,
            "visible_phone_number": visible_phone_number,
            "business_start_hour": business_start_hour,
            "business_end_hour": business_end_hour,
            "road_address": road_address,
            "abbr_address": abbr_address,
            "detail_address": detail_address,
            "short_address": short_address,
            "guide_message": guide_message,
            "latitude": latitude,
            "longitude": longitude,
            "point": Point(longitude, latitude),
            "reservation_availability_option": reservation_availability_option,
            "reservation_change_option": reservation_change_option,
            "daily_pet_limit": daily_pet_limit,
        }

        pet_kindergarden, has_updated = update_model(
            instance=pet_kindergarden,
            fields=list(data.keys()),
            data=data,
        )
        return pet_kindergarden
