from typing import Any

from django.db.models import F, QuerySet, Value
from django.db.models.functions import Concat

from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.pet_kindergardens.selectors.abstracts import (
    AbstractPetKindergardenSelector,
)


class PetKindergardenSelector(AbstractPetKindergardenSelector):
    """
    이 클래스는 반려동물 유치원을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_user(self, user) -> QuerySet[Any]:
        """
        이 함수는 사용자 정보로, 해당 사용자가 속한 유치원 목록을 조회합니다.

        Args:
            user: User: 유저 객체

        Returns:
            QuerySet[Any]: 존재하지 않으면 빈 쿼리셋을 반환
        """

        return (
            PetKindergarden.objects.filter(customers__user=user)
            .annotate(full_address=Concat(F("road_address"), Value(" "), F("detail_address")))
            .values("id", "name", "full_address", "profile_thumbnail_url")
        )

    def get_by_pet_kindergarden_id_for_summary_info(self, pet_kindergarden_id: int) -> QuerySet:
        """
        이 함수는 반려동물 유치원 아이디로 해당 반려동물 유치원의 요약 정보를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디

        Returns:
            Optional[Any]: 반려동물 유치원이 존재하지 않으면 None을 반환
        """

        return PetKindergarden.objects.filter(id=pet_kindergarden_id).values(
            "id", "name", "business_start_hour", "business_end_hour"
        )
