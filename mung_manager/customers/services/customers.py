from django.db import transaction

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import get_object_or_not_found
from mung_manager.commons.services import update_model

from mung_manager.customers.selectors.customers import CustomerSelector
from mung_manager.customers.services.abstracts import AbstractCustomerService
from mung_manager_db.models import Customer


class CustomerService(AbstractCustomerService):
    """이 클래스는 고객을 DB에서 PUSH하는 비즈니스 로직을 담당합니다."""

    def __init__(self, customer_selector: CustomerSelector):
        self._customer_selector = customer_selector

    @transaction.atomic
    def register_customer(
        self,
        user,
        customer_id: int,
    ) -> Customer:
        """
        이 함수는 고객 정보에서 비어있는 user_id 값을 채웁니다.

        Args:
            user: 유저 객체
            customer_id (int): 고객 아이디

        Returns:
            Customer: 고객 객체
        """

        # 고객이 존재하는지 검증
        customer = get_object_or_not_found(
            self._customer_selector.get_by_id(customer_id=customer_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )

        # 유저 id 업데이트
        fields = ["user"]
        data = {"user": user}

        customer, has_updated = update_model(instance=customer, fields=fields, data=data)

        return customer
