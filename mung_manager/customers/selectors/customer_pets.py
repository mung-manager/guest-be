from django.db.models.query import QuerySet

from mung_manager.customers.models import CustomerPet, Customer
from mung_manager.customers.selectors.abstracts import AbstractCustomerPetSelector


class CustomerPetSelector(AbstractCustomerPetSelector):
    """
    이 클래스는 고객 반려동물을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_customer(self, customer: Customer) -> QuerySet[CustomerPet]:
        """
        이 함수는 고객 객체로 해당 반려동물 유치원에 속한 고객의 반려동물 목록을 조회합니다.

        Args:
            customer (Customer): 고객 객체

        Returns:
            QuerySet[CustomerPet]: 등록된 반려동물 목록이 존재하지 않으면 빈 쿼리셋을 반환합니다.
        """
        return CustomerPet.objects.filter(customer=customer, is_deleted=False)
