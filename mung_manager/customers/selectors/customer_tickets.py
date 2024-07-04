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
        customer_tickets = CustomerTicket.objects.filter(
            customer=customer,
            expired_at__gte=timezone.now(),
            unused_count__gt=0,
        ).select_related("ticket")

        time_count = all_day_count = hotel_count = 0
        for customer_ticket in customer_tickets:
            ticket_type = customer_ticket.ticket.ticket_type
            if ticket_type == TicketType.TIME.value:
                time_count += 1
            elif ticket_type == TicketType.ALL_DAY.value:
                all_day_count += 1
            elif ticket_type == TicketType.HOTEL.value:
                hotel_count += 1

        return {
            "time": time_count,
            "all_day": all_day_count,
            "hotel": hotel_count,
        }
