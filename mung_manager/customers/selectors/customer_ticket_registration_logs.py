from django.db.models.query import QuerySet

from mung_manager.customers.models import CustomerTicketRegistrationLog
from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerTicketRegistrationLogSelector,
)


class CustomerTicketRegistrationLogSelector(AbstractCustomerTicketRegistrationLogSelector):
    """이 클래스는 고객 티켓 등록 로그를 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_customer_id_for_ticket_registration_logs(
        self, customer_id: int
    ) -> QuerySet[CustomerTicketRegistrationLog]:
        """고객 아이디로 최신순으로 고객 티켓과 티켓을 포함한 고객 티켓 등록 로그 쿼리셋을 조회합니다.

        Args:
            customer_id (int): 고객 아이디

        Returns:
            QuerySet[CustomerTicketRegistrationLog]: 고객 티켓 등록 로그 쿼리셋이며 없을 경우 빈 쿼리셋을 반환
        """
        return (
            CustomerTicketRegistrationLog.objects.filter(customer_ticket__customer_id=customer_id)
            .select_related("customer_ticket", "customer_ticket__ticket")
            .order_by("-id")
        )
