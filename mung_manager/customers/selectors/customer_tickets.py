from typing import Optional

from django.db.models import F
from django.db.models.query import QuerySet
from django.utils import timezone

from mung_manager.customers.models import CustomerTicket
from mung_manager.customers.selectors.abstracts import AbstractCustomerTicketSelector
from mung_manager.tickets.enums import TicketType


class CustomerTicketSelector(AbstractCustomerTicketSelector):
    """이 클래스는 고객 티켓을 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_by_customer_id_for_ticket_type(self, customer_id: int) -> dict[str, list]:
        """이 함수는 고객 아이디로 예약을 위한 티켓을 포함한 만료기간 및 사용횟수가 남은 고객 티켓을 조회합니다.

        Args:
            customer_id: 고객 아이디

        Returns:
            QuerySet[CustomerTicket]: 고객 티켓 쿼리셋이며 없을 경우 빈 쿼리셋을 반환
        """
        customer_tickets = CustomerTicket.objects.filter(
            customer_id=customer_id,
            expired_at__gte=timezone.now(),
            total_count__gt=F("used_count"),
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

    def get_with_ticket_by_id_and_customer_id(
        self, customer_ticket_id: int, customer_id: int
    ) -> Optional[CustomerTicket]:
        """이 함수는 고객 티켓 아이디와 고객 아이디로 티켓을 포함한 고객 티켓을 조회합니다.

        Args:
            customer_ticket_id: 고객 티켓 아이디
            customer_id: 고객 아이디

        Returns:
            CustomerTicket: 고객 티켓이며 없을 경우 None을 반환
        """
        try:
            return (
                CustomerTicket.objects.filter(id=customer_ticket_id, customer_id=customer_id)
                .select_related("ticket")
                .get()
            )

        except CustomerTicket.DoesNotExist:
            return None

    def get_queryset_for_hotel(self, customer_ticket_ids: list[int], customer_id: int) -> QuerySet[CustomerTicket]:
        """이 함수는 고객 티켓 아이디 리스트와 고객 아이디로 만료 기간 순으로 티켓을 포함한 고객 티켓 리스트를 조회합니다.

        Args:
            customer_ticket_ids: 고객 티켓 아이디 리스트
            customer_id: 고객 아이디

        Returns:
            list[CustomerTicket]: 고객 티켓 리스트
        """
        return (
            CustomerTicket.objects.filter(
                id__in=customer_ticket_ids, customer_id=customer_id, ticket__ticket_type=TicketType.HOTEL.value
            )
            .select_related("ticket")
            .order_by("expired_at")
        )
