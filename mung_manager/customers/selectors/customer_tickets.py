from typing import Any

from django.db.models import QuerySet
from django.utils import timezone

from mung_manager.customers.models import Customer, CustomerTicket
from mung_manager.customers.selectors.abstracts import AbstractCustomerTicketSelector
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
            QuerySet: 소유하고 있는 티켓이 존재하지 않으면 빈 쿼리셋을 반환합니다.
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

    def get_queryset_by_customer_and_ticket_type(self, customer: Customer, ticket_type: str) -> QuerySet[Any]:
        """
        고객 객체와 티켓 타입으로 해당 고객이 소유하고 있는 티켓 타입 중 만료되지 않은 티켓의 목록을 조회합니다.

        Args:
            customer (Customer): 고객 객체
            ticket_type: 티켓 타입

        Returns:
            QuerySet: 소유하고 있는 티켓이 존재하지 않으면 빈 쿼리셋을 반환합니다.
        """
        return (
            CustomerTicket.objects.filter(
                customer=customer,
                expired_at__gte=timezone.now(),
                unused_count__gt=0,
                ticket__ticket_type=ticket_type,
            )
            .select_related("ticket")
            .order_by("-expired_at")
        )
