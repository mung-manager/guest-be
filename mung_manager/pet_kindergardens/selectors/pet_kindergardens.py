from typing import Any, Optional

from django.db.models import F, QuerySet, Value
from django.db.models.functions import Concat
from django_stubs_ext import ValuesQuerySet
from typing_extensions import Annotated

from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.pet_kindergardens.selectors.abstracts import (
    AbstractPetKindergardenSelector,
)
from mung_manager.pet_kindergardens.types import full_address_type


class PetKindergardenSelector(AbstractPetKindergardenSelector):
    """
    이 클래스는 반려동물 유치원을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_by_id_and_user_id(self, pet_kindergarden_id: int, user_id: int) -> Optional[PetKindergarden]:
        """
        이 함수는 유저 아이디와 반려동물 유치원 아이디로 유치원 객체를 조회합니다.

        Args:
            pet_kindergarden_id: int: 유치원 아이디
            user_id: int: 유저 아이디

        Returns:
            Optional[PetKindergarden]: 유치원 객체 또는 None
        """
        try:
            return PetKindergarden.objects.filter(id=pet_kindergarden_id, customers__user_id=user_id).get()
        except PetKindergarden.DoesNotExist:
            return None

    def get_queryset_by_user(self, user) -> QuerySet[Annotated[PetKindergarden, full_address_type], dict[str, Any]]:
        """
        이 함수는 사용자 정보로, 해당 사용자가 속한 유치원 목록을 조회합니다.

        Args:
            user: User: 유저 객체

        Returns:
            QuerySet[QuerySet[Annotated[PetKindergarden, full_address_type], dict[str, Any]]: 정의된 반환값
        """

        return (
            PetKindergarden.objects.filter(customers__user=user)
            .annotate(full_address=Concat(F("road_address"), Value(" "), F("detail_address")))
            .values("id", "name", "full_address", "profile_thumbnail_url")
        )

    def get_by_pet_kindergarden_id_for_reservation_availability_option(
        self, pet_kindergarden_id: int
    ) -> ValuesQuerySet[PetKindergarden, str]:
        """
        이 함수는 반려동물 유치원 아이디로 해당 반려동물 유치원의 당일 예약 가능 설정을 조회합니다.

        Args:
            pet_kindergarden_id: 반려동물 유치원 아이디

        Returns:
            ValuesQuerySet[PetKindergarden, str]: 존재하지 않으면 빈 쿼리셋을 반환
        """
        return PetKindergarden.objects.filter(id=pet_kindergarden_id).values_list(
            "reservation_availability_option", flat=True
        )

    def get_by_pet_kindergarden_id_for_daily_pet_limit(self, pet_kindergarden_id: int) -> int:
        """
        이 함수는 반려동물 유치원 아이디로 해당 반려동물 유치원의 일일 최대 반려동물 수를 조회합니다.

        Args:
            pet_kindergarden_id: 반려동물 유치원 아이디

        Returns:
            int: 일일 최대 반려동물 수 반환
        """
        return PetKindergarden.objects.filter(id=pet_kindergarden_id).values_list("daily_pet_limit", flat=True).get()
