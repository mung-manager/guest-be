from typing import List

from django.db.models import Q
from django.db.models.query import QuerySet

from mung_manager.customers.models import CustomerPet
from mung_manager.customers.selectors.abstracts import AbstractCustomerPetSelector


class CustomerPetSelector(AbstractCustomerPetSelector):
    """이 클래스는 고객 반려동물을 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_names_and_customer_id_for_undeleted_customer_pet(
        self, names: List[str], customer_id: int
    ) -> QuerySet[CustomerPet]:
        """고객 반려동물 아이디로 삭제되지 않은 고객 반려동물을 가져옵니다.

        Args:
            customer_pet_id (int): 고객 반려동물 아이디

        Returns:
            CustomerPet: 삭제되지 않은 고객 반려동물
        """
        return CustomerPet.objects.filter(
            name__in=names,
            customer_id=customer_id,
            is_deleted=False,
            deleted_at__isnull=True,
        )

    def exists_by_names_and_customer_id_for_undeleted_customer_pet(self, names: List[str], customer_id: int) -> bool:
        """반려동물 이름들과 고객 아이디로 삭제되지 않은 고객 반려동물이 존재하는지 확인합니다.

        Args:
            names (List[str]): 반려동물 이름 리스트
            customer_id (int): 고객 아이디

        Returns:
            bool: 고객 반려동물이 존재하면 True, 아니면 False를 반환
        """
        return CustomerPet.objects.filter(
            name__in=names,
            customer_id=customer_id,
            is_deleted=False,
            deleted_at__isnull=True,
        ).exists()

    def get_by_keyword_for_search(self, keyword: str) -> QuerySet[CustomerPet]:
        """이 함수는 키워드로 고객을 포함한 삭제되지 않은 고객 반려동물 조회합니다.
        키워드는 고객 이름, 고객 전화번호, 고객 반려동물 이름을 검색합니다.

        Args:
            keyword (str): 검색 키워드

        Returns:
            QuerySet[Customer]: 고객 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return (
            CustomerPet.objects.filter(is_deleted=False, deleted_at__isnull=True)
            .filter(
                Q(customer__name__icontains=keyword)
                | Q(customer__phone_number__icontains=keyword)
                | Q(name__icontains=keyword)
            )
            .filter(customer__is_active=True)
            .select_related("customer")
        )
