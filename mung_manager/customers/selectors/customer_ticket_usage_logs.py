from django.db.models.query import QuerySet

from mung_manager.customers.models import CustomerTicketUsageLog
from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerTicketUsageLogSelector,
)


class CustomerTicketUsageLogSelector(AbstractCustomerTicketUsageLogSelector):
    """
    이 클래스는 고객 티켓 사용 로그를 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_reservation_ids(self, reservation_ids: list[int]) -> QuerySet[CustomerTicketUsageLog]:
        """
        예약 아이디 리스트로 고객 티켓 사용 로그 쿼리셋을 조회합니다.

        Args:
            reservation_ids (list[int]): 예약 아이디 리스트

        Returns:
            QuerySet[CustomerTicketUsageLog]: 고객 티켓 사용 로그 쿼리셋이며 없을 경우 빈 쿼리셋을 반환

        """
        return CustomerTicketUsageLog.objects.filter(reservation_id__in=reservation_ids)
