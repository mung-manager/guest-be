from collections import defaultdict
from typing import Annotated, Any, Optional

from django.db import connection
from django.db.models import Case, CharField, F, QuerySet, Value, When
from django.utils import timezone

from mung_manager.customers.models import Customer
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.enums import ReservationStatus
from mung_manager.reservations.models import Reservation
from mung_manager.reservations.selectors.abstracts import AbstractReservationSelector
from mung_manager.reservations.types import attendance_type
from mung_manager.tickets.enums import TicketStatus, TicketType


class ReservationSelector(AbstractReservationSelector):
    """
    이 클래스는 예약을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    @staticmethod
    def find_root(reservation):
        current = reservation
        while current.parent_id is not None:
            current = current.parent
        return current

    def get_queryset_by_customer_and_pet_kindergarden(
        self, customer: Customer, pet_kindergarden: PetKindergarden
    ) -> list[dict[str, Any]]:
        """
        고객 객체와 반려동물 유치원 객체로 등원 예정인 예약 목록을 조회합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체

        Returns:
            list[dict[str, Any]]: 예약 리스트 반환
        """
        reservations = Reservation.objects.filter(
            customer=customer,
            pet_kindergarden=pet_kindergarden,
            reserved_at__gt=timezone.now(),
            reservation_status=ReservationStatus.COMPLETED.value,
        ).select_related("customer_pet")

        reservation_list = []

        # 각 예약을 그룹화
        grouped_reservations = defaultdict(list)
        for reservation in reservations:
            reservation_id = reservation.id
            if reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value and reservation.is_extented:
                root_reservation = self.find_root(reservation)
                reservation_id = root_reservation.id
            grouped_reservations[reservation_id].append(reservation)

        # 그룹화된 예약 정보를 딕셔너리로 변환
        for group in grouped_reservations.values():
            if len(group) == 1 and group[0].customer_ticket.ticket.ticket_type != TicketType.HOTEL.value:
                reservation = group[0]
                ticket_type_value = reservation.customer_ticket.ticket.ticket_type
                ticket_type = (
                    TicketType.TIME.value if ticket_type_value == TicketType.TIME.value else TicketType.ALL_DAY.value
                )
                reservation_data = {
                    "ticket_type": ticket_type,
                    "start_at": reservation.reserved_at,
                    "end_at": reservation.end_at,
                    "customer_pet_name": reservation.customer_pet.name,
                }
            else:
                ticket_type = TicketType.HOTEL.value
                start_time = min(res.reserved_at for res in group)  # type: ignore
                end_time = max(res.end_at for res in group)  # type: ignore
                reservation_data = {
                    "ticket_type": ticket_type,
                    "start_at": start_time,
                    "end_at": end_time,
                    "customer_pet_name": group[0].customer_pet.name,
                }

            reservation_list.append(reservation_data)

        return reservation_list

    def get_queryset_by_customer_and_pet_kindergarden_for_detail(
        self, customer: Customer, pet_kindergarden: PetKindergarden, ticket_status: str
    ) -> QuerySet[Annotated[Reservation, attendance_type]] | list[dict[str, Any]]:
        """
        고객 객체와 반려동물 유치원 객체로 등원 예정인 예약 상세 목록을 조회합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            ticket_status (str): 티켓 상태

        Returns:
            QuerySet[Annotated[Reservation, attendance_type]] | list[dict[str, Any]]: 정의된 응답 스키마 및 예약 리스트 반환
        """
        reservations = self.generate_reservation_queryset(customer, pet_kindergarden, ticket_status)

        # 연박이 없는 경우
        if not reservations.filter(is_extented=True).exists():
            return reservations.annotate(
                reservation_id=F("id"),
                ticket_type=F("customer_ticket__ticket__ticket_type"),
                customer_pet_name=F("customer_pet__name"),
                reservation_change_option=F("pet_kindergarden__reservation_change_option"),
                price=F("customer_ticket__ticket__price"),
                usage_time=F("customer_ticket__ticket__usage_time"),
                used_ticket_count=F("customer_ticket__ticket__usage_count"),
            ).values(
                "reservation_id",
                "ticket_type",
                "created_at",
                "reserved_at",
                "customer_pet_name",
                "is_attended",
                "usage_time",
                "used_ticket_count",
                "price",
                "reservation_change_option",
                "attendance_status",
            )

        return self.group_reservations_by_ticket_type(reservations)

    @staticmethod
    def group_reservations_by_ticket_type(reservations):
        """
        각 예약을 그룹화합니다.

        Args:
            reservations (QuerySet): 예약 쿼리셋

        Returns:
            list[dict[str, Any]]: 그룹화된 예약 리스트
        """
        grouped_reservations = defaultdict(list)
        accumulate_count = defaultdict(int)

        for reservation in reservations:
            reservation_id = reservation.id
            if reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value and reservation.is_extented:
                root_reservation = ReservationSelector.find_root(reservation)
                reservation_id = root_reservation.id
                accumulate_count[reservation_id] += 1

            grouped_reservations[reservation_id].append(reservation)

        reservation_list = []
        for reservation_id, group in grouped_reservations.items():
            reservation = group[0]
            ticket_type = reservation.customer_ticket.ticket.ticket_type

            reservation_data = {
                "reservation_id": reservation_id,
                "ticket_type": ticket_type,
                "created_at": reservation.created_at,
                "reserved_at": reservation.reserved_at,
                "customer_pet_name": reservation.customer_pet.name,
                "is_attended": reservation.is_attended,
                "reservation_change_option": reservation.pet_kindergarden.reservation_change_option,
                "attendance_status": reservation.attendance_status,
                "price": reservation.customer_ticket.ticket.price,
                "used_ticket_count": 1,
            }

            if ticket_type == TicketType.TIME.value:
                reservation_data["usage_time"] = reservation.customer_ticket.ticket.usage_time
            elif ticket_type == TicketType.HOTEL.value:
                reservation_data["usage_time"] = None
                reservation_data["used_ticket_count"] = accumulate_count[reservation_id]
                reservation_data["created_at"] = min(res.created_at for res in group)
                reservation_data["reserved_at"] = min(res.reserved_at for res in group)

            reservation_list.append(reservation_data)

        return reservation_list

    @staticmethod
    def generate_reservation_queryset(customer, pet_kindergarden, ticket_status):
        """
        티켓 상태에 따른 예약 쿼리셋을 생성합니다.

        Args:
            customer (Customer): 고객 객체
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            ticket_status (str): 티켓 상태

        Returns:
            QuerySet: 예약 쿼리셋
        """
        reservations = Reservation.objects.none()
        if ticket_status == TicketStatus.PENDING.value:
            reservations = Reservation.objects.filter(
                customer=customer,
                pet_kindergarden=pet_kindergarden,
                reserved_at__gt=timezone.now(),
                reservation_status=ReservationStatus.COMPLETED.value,
            ).select_related("customer_pet")
        elif ticket_status == TicketStatus.COMPLETED.value:
            reservations = Reservation.objects.filter(
                customer=customer,
                pet_kindergarden=pet_kindergarden,
                reserved_at__lt=timezone.now(),
                reservation_status=ReservationStatus.COMPLETED.value,
            ).select_related("customer_pet")

        reservations = reservations.annotate(
            attendance_status=Case(
                When(reserved_at__gt=timezone.now(), then=Value("등원 전")),
                When(is_attended=True, then=Value("등원 완료")),
                When(reserved_at__lt=timezone.now(), is_attended=False, then=Value("결석")),
                default=Value(""),
                output_field=CharField(),
            ),
        )
        return reservations

    def get_by_id_for_uncanceled_reservation(self, reservation_id: int) -> Optional[Reservation]:
        """
        예약 아이디로 취소되지 않은 예약을 조회합니다.

        Args:
            reservation_id (int): 예약 아이디

        Returns:
            Optional[Reservation]: 예약이 존재하면 예약 객체를 반환하고, 존재하지 않으면 None을 반환
        """
        try:
            return Reservation.objects.get(id=reservation_id, reservation_status=ReservationStatus.COMPLETED.value)

        except Reservation.DoesNotExist:
            return None

    def get_child_ids_by_parent_id(self, parent_id: int) -> list[tuple[int, None]]:
        """
        부모 예약 아이디로 모든 자식 예약 아이디를 조회합니다.

        Args:
            parent_id (int): 부모 예약 아이디

        Returns:
            list[tuple[int, int]]: 부모 예약 아이디와 모든 자식 예약 아이디를 튜플로 반환
        """
        with connection.cursor() as cursor:
            query = """
            WITH RECURSIVE CTE AS (
                -- Anchor member: This selects the initial parent_id
                SELECT reservation_id,parent_id
                FROM reservation
                WHERE parent_id = %s

                UNION ALL

                -- Recursive member: This joins the table to itself
                SELECT r.reservation_id, r.parent_id
                FROM reservation r
                INNER JOIN CTE c ON r.parent_id = c.reservation_id
            )
            SELECT reservation_id
            FROM CTE;
            """
            cursor.execute(query, [parent_id])
            result = cursor.fetchall()
        return result

    def get_queryset_with_customer_ticket_and_ticket_by_ids(self, reservation_ids: list[int]) -> QuerySet[Reservation]:
        """
        예약 아이디 리스트로 고객 티켓과 티켓을 포함한 예약 쿼리셋을 조회합니다.

        Args:
            reservation_ids (list[int]): 예약 아이디 리스트

        Returns:
            QuerySet[Reservation]: 예약 쿼리셋을 반환이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return Reservation.objects.filter(id__in=reservation_ids).select_related(
            "customer_ticket", "customer_ticket__ticket"
        )
