from typing import Any

from django.db.models import F, QuerySet, Value
from django.db.models.functions import Concat
from django_stubs_ext import WithAnnotations
from django_stubs_ext.aliases import ValuesQuerySet

from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.pet_kindergardens.selectors.abstracts import (
    AbstractPetKindergardenSelector,
)
from mung_manager.pet_kindergardens.types import info_for_full_address, info_for_summary


class PetKindergardenSelector(AbstractPetKindergardenSelector):
    """
    이 클래스는 반려동물 유치원을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_user(
        self, user
    ) -> QuerySet[WithAnnotations[PetKindergarden, info_for_full_address], dict[str, Any]]:
        """
        이 함수는 사용자 정보로, 해당 사용자가 속한 유치원 목록을 조회합니다.

        Args:
            user: User: 유저 객체

        Returns:
            QuerySet[WithAnnotations[PetKindergarden, info_for_full_address], dict[str, Any]]: 정의된 응답 스키마
        """

        return (
            PetKindergarden.objects.filter(customers__user=user)
            .annotate(full_address=Concat(F("road_address"), Value(" "), F("detail_address")))
            .values("id", "name", "full_address", "profile_thumbnail_url")
        )

    def get_by_pet_kindergarden_id_for_summary_info(
        self, pet_kindergarden_id: int
    ) -> ValuesQuerySet[PetKindergarden, info_for_summary]:
        """
        이 함수는 반려동물 유치원 아이디로 해당 반려동물 유치원의 요약 정보를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디

        Returns:
            ValuesQuerySet[PetKindergarden, info_for_summary]: 정의된 응답 스키마
        """

        return PetKindergarden.objects.filter(id=pet_kindergarden_id).values(
            "id", "name", "business_start_hour", "business_end_hour"
        )
