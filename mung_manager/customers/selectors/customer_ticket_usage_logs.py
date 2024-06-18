from typing import Optional

from django.db.models.query import QuerySet

from mung_manager.customers.models import CustomerTicketUsageLog
from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerTicketUsageLogSelector,
)


class CustomerTicketUsageLogSelector(AbstractCustomerTicketUsageLogSelector):
    """이 클래스는 고객 티켓 사용 로그를 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_customer_id_for_ticket_usage_logs(self, customer_id: int) -> QuerySet[CustomerTicketUsageLog]:
        """고객 아이디로 최신순으로 예약과 고객 티켓을 포함한 고객 티켓 사용 로그 쿼리셋을 조회합니다.

        Args:
            customer_id (int): 고객 아이디

        Returns:
            QuerySet[CustomerTicketUsageLog]: 고객 티켓 사용 로그 쿼리셋이며 없을 경우 빈 쿼리셋을 반환

        """
        return (
            CustomerTicketUsageLog.objects.filter(customer_ticket__customer_id=customer_id)
            .select_related("reservation", "customer_ticket", "customer_ticket__ticket")
            .order_by("-id")
        )

    def get_queryset_by_reservation_ids(self, reservation_ids: list[int]) -> QuerySet[CustomerTicketUsageLog]:
        """예약 아이디 리스트로 고객 티켓 사용 로그 쿼리셋을 조회합니다.

        Args:
            reservation_ids (list[int]): 예약 아이디 리스트

        Returns:
            QuerySet[CustomerTicketUsageLog]: 고객 티켓 사용 로그 쿼리셋이며 없을 경우 빈 쿼리셋을 반환

        """
        return CustomerTicketUsageLog.objects.filter(reservation_id__in=reservation_ids)

    def get_by_reservation_id(self, reservation_id: int) -> Optional[CustomerTicketUsageLog]:
        """예약 아이디로 고객 티켓 사용 로그를 조회합니다.

        Args:
            reservation_id (int): 예약 아이디

        Returns:
            Optional[CustomerTicketUsageLog]: 고객 티켓 사용 로그이며 없을 경우 None을 반환

        """
        try:
            return CustomerTicketUsageLog.objects.filter(reservation_id=reservation_id).get()
        except CustomerTicketUsageLog.DoesNotExist:
            return None
