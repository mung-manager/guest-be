import re
from collections import defaultdict
from operator import itemgetter
from typing import Any

from mung_manager.customers.serializers import CustomerTicketSerializer
from mung_manager.reservations.services.abstracts import AbstractReservationService


class ReservationService(AbstractReservationService):
    """
    이 클래스는 예약을 DB에 PUSH하는 비즈니스 로직을 담당합니다.
    """

    @staticmethod
    def group_and_sort_tickets(tickets) -> dict[Any, list]:
        tickets_data = CustomerTicketSerializer(tickets, many=True).data
        grouped_tickets = defaultdict(list)
        for ticket in tickets_data:
            grouped_tickets[ticket["full_ticket_type"]].append(ticket)
        for ticket_type in grouped_tickets:
            grouped_tickets[ticket_type] = sorted(grouped_tickets[ticket_type], key=itemgetter("expired_at"))
        sorted_grouped_tickets = dict(
            sorted(grouped_tickets.items(), key=lambda item: (not bool(re.match(r"^\d", item[0])), item[0]))
        )
        return sorted_grouped_tickets
