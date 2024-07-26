from typing import Annotated, Any, Optional

from django.db.models import (
    BooleanField,
    Case,
    CharField,
    F,
    IntegerField,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Concat
from django.utils import timezone

from mung_manager.customers.models import Customer, CustomerTicket
from mung_manager.customers.selectors.abstracts import AbstractCustomerTicketSelector
from mung_manager.customers.types import is_expired_type
from mung_manager.tickets.enums import TicketType


class CustomerTicketSelector(AbstractCustomerTicketSelector):
    """
    이 클래스는 고객 티켓을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_queryset_by_customer(self, customer: Customer) -> dict[str, QuerySet]:
        """
        고객 객체로 해당 고객이 소유하고 있는 만료되지 않은 잔여 티켓 타입의 목록을 조회합니다

        Args:
            customer (Customer): 고객 객체

        Returns:
            dict[str, list[str]]: 정의된 반환값
        """
        customer_ticket_types = (
            CustomerTicket.objects.filter(
                customer=customer,
                expired_at__gte=timezone.now(),
                unused_count__gt=0,
            )
            .select_related("ticket")
            .annotate(
                full_ticket_type=Case(
                    When(
                        ticket__ticket_type=TicketType.TIME.value,
                        then=Concat(F("ticket__usage_time"), Value("시간"), output_field=CharField()),
                    ),
                    default=F("ticket__ticket_type"),
                    output_field=CharField(),
                ),
                sort_order=Case(
                    When(ticket__ticket_type=TicketType.TIME.value, then=F("ticket__usage_time")),
                    When(full_ticket_type="종일", then=Value(98)),
                    When(full_ticket_type="호텔", then=Value(99)),
                    default=Value(100),
                    output_field=IntegerField(),
                ),
            )
            .order_by("sort_order", "full_ticket_type")
            .values_list("full_ticket_type", flat=True)
            .distinct()
        )

        return {"ticket_types": customer_ticket_types}

    def get_queryset_by_customer_and_ticket_type_for_ticket_detail(
        self, customer: Customer, ticket_type: str
    ) -> QuerySet[CustomerTicket]:
        """
        고객 객체와 티켓 타입으로 해당 고객이 소유하고 있는 만료되지 않은 티켓의 상세 정보를 조회합니다.

        Args:
            customer (Customer): 고객 객체
            ticket_type (str): 티켓 타입

        Returns:
            QuerySet[CustomerTicket]: 존재하지 않으면 빈 쿼리셋 반환
        """
        if ticket_type in [TicketType.ALL_DAY.value, TicketType.HOTEL.value]:
            usage_time, ticket_type = "0", ticket_type
        else:
            usage_time, ticket_type = ticket_type[:-2], ticket_type[-2:]

        return CustomerTicket.objects.filter(
            customer=customer,
            expired_at__gte=timezone.now(),
            unused_count__gt=0,
            ticket__usage_time=usage_time,
            ticket__ticket_type=ticket_type,
        ).select_related("ticket")

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

    def get_queryset_by_customer_for_hotel_ticket_type(self, customer: Customer) -> QuerySet[CustomerTicket]:
        """
        고객 객체로 해당 고객이 소유하고 있는 만료되지 않은 호텔 타입의 티켓 목록을 조회합니다.

        Args:
            customer (Customer): 고객 객체

        Returns:
            QuerySet[CustomerTicket]: 소유하고 있는 티켓이 존재하지 않으면 빈 쿼리셋을 반환합니다.
        """

        return CustomerTicket.objects.filter(
            customer=customer,
            expired_at__gte=timezone.now(),
            unused_count__gt=0,
            ticket__ticket_type=TicketType.HOTEL.value,
            ticket__usage_time=0,
        ).select_related("ticket")

    def get_for_all_day_or_time_ticket_type(
        self, customer: Customer, ticket_type: str, ticket_id: Optional[int]
    ) -> Optional[CustomerTicket]:
        """
        고객 객체와 티켓 아이디, 티켓 타입으로 해당 고객이 소유하고 있는 (호텔 타입이 아닌) 티켓을 조회합니다.

        Args:
            customer (Customer): 고객 객체
            ticket_type (str): 티켓 타입
            ticket_id (int): 티켓 아이디

        Returns:
            Optional[CustomerTicket]: 소유하고 있는 티켓이 존재하지 않으면 None을 반환합니다.
        """

        if ticket_type.endswith(TicketType.TIME.value):
            type_value = ticket_type[-2:]
            time_value = int(ticket_type[:-2])
        else:
            type_value = ticket_type
            time_value = 0

        try:
            return CustomerTicket.objects.select_related("ticket").get(
                id=ticket_id,
                customer=customer,
                expired_at__gte=timezone.now(),
                unused_count__gt=0,
                ticket__ticket_type=type_value,
                ticket__usage_time=time_value,
            )
        except CustomerTicket.DoesNotExist:
            return None

    def get_with_ticket_by_id_and_customer_id(
        self, customer_ticket_id: int, customer_id: int
    ) -> Optional[CustomerTicket]:
        """
        이 함수는 고객 티켓 아이디와 고객 아이디로 티켓을 포함한 고객 티켓을 조회합니다.

        Args:
            customer_ticket_id (int): 고객 티켓 아이디
            customer_id (int): 고객 아이디

        Returns:
            Optional[CustomerTicket]: 고객 티켓이 존재하지 않을 경우 None 반환
        """
        try:
            return (
                CustomerTicket.objects.filter(id=customer_ticket_id, customer_id=customer_id)
                .select_related("ticket")
                .get()
            )

        except CustomerTicket.DoesNotExist:
            return None

    def get_by_customer_ticket_id_for_unused_count(self, customer_ticket_id: int) -> Optional[int]:
        """
        이 함수는 티켓 아이디로 티켓의 잔여 횟수를 조회합니다.

        Args:
            customer_ticket_id (int): 고객 티켓 아이디

        Returns:
            Optional[int]: 고객 티켓이 존재하지 않을 경우 None 반환
        """
        try:
            return CustomerTicket.objects.filter(id=customer_ticket_id).values_list("unused_count", flat=True).get()

        except CustomerTicket.DoesNotExist:
            return None
