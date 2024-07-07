from typing import Annotated, Any

from django.db.models import (
    BooleanField,
    Case,
    IntegerField,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)
from django.utils import timezone

from mung_manager.customers.models import Customer, CustomerTicket
from mung_manager.customers.selectors.abstracts import AbstractCustomerTicketSelector
from mung_manager.customers.types import is_expired_type
from mung_manager.tickets.enums import TicketType


class CustomerTicketSelector(AbstractCustomerTicketSelector):
    """
    이 클래스는 고객 티켓을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_customer(self, customer: Customer) -> dict[str, list]:
        """
        고객 객체로 해당 고객이 소유하고 있는 만료되지 않은 티켓의 목록을 조회합니다.

        Args:
            customer (Customer): 고객 객체

        Returns:
            dict[str, list]: 정의된 반환값
        """
        customer_tickets = CustomerTicket.objects.filter(
            customer=customer,
            expired_at__gte=timezone.now(),
            unused_count__gt=0,
        ).select_related("ticket")

        time_customer_tickets = []
        all_day_customer_tickets = []
        hotel_customer_tickets = []
        for customer_ticket in customer_tickets:
            ticket_type = customer_ticket.ticket.ticket_type
            if ticket_type == TicketType.TIME.value:
                time_customer_tickets.append(customer_ticket)
            elif ticket_type == TicketType.ALL_DAY.value:
                all_day_customer_tickets.append(customer_ticket)
            elif ticket_type == TicketType.HOTEL.value:
                hotel_customer_tickets.append(customer_ticket)

        return {
            "time": time_customer_tickets,
            "all_day": all_day_customer_tickets,
            "hotel": hotel_customer_tickets,
        }

    def get_by_customer_for_count(self, customer: Customer) -> dict[str, int]:
        """
        고객 객체로 해당 고객이 소유하고 있는 만료되지 않은 티켓 타입별 개수를 조회합니다.

        Args:
            customer (Customer): 고객 객체

        Returns:
            dict[str, int]: 정의된 반환값
        """
        return CustomerTicket.objects.filter(
            customer=customer,
            expired_at__gte=timezone.now(),
            unused_count__gt=0,
        ).aggregate(
            time_count=Sum(
                Case(
                    When(ticket__ticket_type=TicketType.TIME.value, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            all_day_count=Sum(
                Case(
                    When(ticket__ticket_type=TicketType.ALL_DAY.value, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            hotel_count=Sum(
                Case(
                    When(ticket__ticket_type=TicketType.HOTEL.value, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )

    def get_queryset_by_customer_for_parchase_list(
        self, customer: Customer
    ) -> QuerySet[Annotated[CustomerTicket, is_expired_type], dict[str, Any]]:
        """
        고객의 아이디로 해당 고객이 구매한 티켓 목록과 상태를 조회합니다.

        Args:
            customer (Customer): 고객 아이디

        Returns:
            QuerySet[Annotated[CustomerTicket, is_expired_type], dict[str, Any]]: 정의된 반환값
        """

        return (
            CustomerTicket.objects.filter(customer=customer)
            .select_related("ticket")
            .annotate(
                is_expired=Case(
                    When(Q(expired_at__lt=timezone.now()) | Q(unused_count=0), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .values(
                "ticket__ticket_type",
                "ticket__usage_time",
                "ticket__usage_count",
                "is_expired",
                "ticket__price",
                "created_at",
                "expired_at",
            )
        )
