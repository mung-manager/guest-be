from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import (
    check_object_or_not_found,
    get_object_or_not_found,
)
from mung_manager.customers.models import CustomerTicket, CustomerTicketRegistrationLog
from mung_manager.customers.selectors.customers import CustomerSelector
from mung_manager.customers.services.abstracts import AbstractCustomerTicketService
from mung_manager.errors.exceptions import ValidationException
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.tickets.selectors.tickets import TicketSelector


class CustomerTicketService(AbstractCustomerTicketService):
    """이 클래스는 고객의 티켓을 Db에서 PUSH하는 비즈니스 로직을 담당합니다."""

    def __init__(
        self,
        customer_selector: CustomerSelector,
        pet_kindergarden_selector: PetKindergardenSelector,
        ticket_selector: TicketSelector,
    ):
        self._customer_selector = customer_selector
        self._pet_kindergarden_selector = pet_kindergarden_selector
        self._ticket_selector = ticket_selector

    @transaction.atomic
    def register_ticket(self, user, customer_id: int, pet_kindergarden_id: int, ticket_id: int) -> CustomerTicket:
        """이 함수는 고객의 티켓을 검증 후 등록 후 로그를 남깁니다.

        Args:
            user: 유저 객체
            customer_id (int): 고객 아이디
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            ticket_id (int): 티켓 아이디

        Returns:
            CustomerTicket: 고객의 티켓 객체
        """
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )
        customer = get_object_or_not_found(
            self._customer_selector.get_by_id(customer_id=customer_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )

        if customer.is_active is False:
            raise ValidationException(
                detail=SYSTEM_CODE.message("INACTIVE_CUSTOMER"),
                code=SYSTEM_CODE.code("INACTIVE_CUSTOMER"),
            )

        ticket = get_object_or_not_found(
            self._ticket_selector.get_by_pet_id_for_undeleted_ticket(ticket_id=ticket_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
            code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
        )

        customer_ticket = CustomerTicket.objects.create(
            customer_id=customer_id,
            ticket_id=ticket_id,
            expired_at=timezone.now() + timedelta(days=ticket.usage_period_in_days_count),
            total_count=ticket.usage_count,
            unused_count=ticket.usage_count,
            used_count=0,
        )

        # 고객 티켓 등록 로그 생성
        CustomerTicketRegistrationLog.objects.create(
            customer_ticket_id=customer_ticket.id,
        )

        return customer_ticket
