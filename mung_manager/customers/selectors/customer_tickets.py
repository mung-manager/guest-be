from django.db.models import Case, CharField, F, Value, When
from django.db.models.functions import Cast, Concat
from django.db.models.query import QuerySet

from mung_manager.customers.models import Customer, CustomerTicket
from mung_manager.tickets.enums import TicketType

from mung_manager.customers.selectors.abstracts import AbstractCustomerTicketSelector


class CustomerTicketSelector(AbstractCustomerTicketSelector):
    """
    이 클래스는 고객 티켓을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_customer(self, customer) -> QuerySet:
        """
        고객 객체로 해당 고객이 소유하고 있는 만료되지 않은 티켓의 목록을 조회합니다.

        Args:
            customer (Customer): 고객 객체

        Returns:
            QuerySet: 소유하고 있는 티켓이 존재하지 않으면 빈 쿼리셋을 반환합니다.
        """
        return (
            CustomerTicket.objects.filter(customer=customer)
            .filter(unused_count__gt=0)
            .select_related("ticket")
            .annotate(
                full_ticket_type=Case(
                    When(
                        ticket__ticket_type=TicketType.TIME.value,
                        then=Concat(Cast(F("ticket__usage_time"), output_field=CharField()), Value("시간 이용권")),
                    ),
                    default=Concat(Cast(F("ticket__ticket_type"), output_field=CharField()), Value(" 이용권")),
                    output_field=CharField(),
                ),
            )
            .values("id", "full_ticket_type", "unused_count", "expired_at")
        )
