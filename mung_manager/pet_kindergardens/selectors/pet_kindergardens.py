from typing import Any, Optional

from django.db.models import F, QuerySet, Value
from django.db.models.functions import Concat
from typing_extensions import Annotated

from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.pet_kindergardens.selectors.abstracts import (
    AbstractPetKindergardenSelector,
)
from mung_manager.pet_kindergardens.types import info_for_full_address


class PetKindergardenSelector(AbstractPetKindergardenSelector):
    """
    이 클래스는 반려동물 유치원을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_by_id(self, pet_kindergarden_id: int) -> Optional[PetKindergarden]:
        try:
            return PetKindergarden.objects.filter(id=pet_kindergarden_id).get()
        except PetKindergarden.DoesNotExist:
            return None

    def get_queryset_by_user(self, user) -> QuerySet[Annotated[PetKindergarden, info_for_full_address], dict[str, Any]]:
        """
        이 함수는 사용자 정보로, 해당 사용자가 속한 유치원 목록을 조회합니다.

        Args:
            user: User: 유저 객체

        Returns:
            QuerySet[QuerySet[Annotated[PetKindergarden, info_for_full_address], dict[str, Any]]: 정의된 반환값
        """

        return (
            PetKindergarden.objects.filter(customers__user=user)
            .annotate(full_address=Concat(F("road_address"), Value(" "), F("detail_address")))
            .values("id", "name", "full_address", "profile_thumbnail_url")
        )
