from typing import Optional

from django.db.models.query import QuerySet

from mung_manager.customers.models import Customer
from mung_manager.customers.selectors.abstracts import AbstractCustomerSelector


class CustomerSelector(AbstractCustomerSelector):
    """
    이 클래스는 고객을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        이 함수는 고객 아이디로 고객을 가져옵니다.

        Args:
            customer_id (int): 고객 아이디

        Returns:
            Optional[Customer]: 고객 객체이며 존재하지 않으면 None을 반환
        """

        try:
            return Customer.objects.filter(id=customer_id).get()
        except Customer.DoesNotExist:
            return None

    def get_queryset_by_phone_number_and_user_id_is_null(self, phone_number: str) -> QuerySet[Customer]:
        """
        이 함수는 전화번호를 기준으로 user_id가 NULL인 고객 정보를 조회합니다.

        Args:
            phone_number (str): 고객 전화번호

        Returns:
            QuerySet[Customer]: 고객 리스트 쿼리셋이며 존재하지 않으면 빈 쿼리셋을 반환
        """

        return Customer.objects.filter(phone_number=phone_number, user_id__isnull=True)
