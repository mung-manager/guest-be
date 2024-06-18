from django.db.models.query import QuerySet

from mung_manager.pet_kindergardens.models import RawPetKindergarden
from mung_manager.pet_kindergardens.selectors.abstracts import (
    AbstractRawPetKindergardenSelector,
)


class RawPetKindergardenSelector(AbstractRawPetKindergardenSelector):
    """이 클래스는 로우 반려동물 유치원을 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_name(self, name: str) -> QuerySet[RawPetKindergarden]:
        """
        이 함수는 이름으로 로우 반려동물 유치원 쿼리셋을 조회합니다.

        Args:
            name: 반려동물 유치원 이름

        Returns:
            QuerySet[RawPetKindergarden]: 로우 반려동물 유치원 쿼리셋 존재하지 않으면 빈 쿼리셋을 반환
        """
        return RawPetKindergarden.objects.filter(name__icontains=name)
