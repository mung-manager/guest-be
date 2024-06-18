from typing import Optional

from django.db import connection
from django.db.models import DateField, Q
from django.db.models.functions import Cast
from django.db.models.query import QuerySet

from mung_manager.reservations.enums import ReservationStatus
from mung_manager.reservations.models import Reservation
from mung_manager.reservations.selectors.abstracts import AbstractReservationSelector
from mung_manager.tickets.enums import TicketType


class ReservationSelector(AbstractReservationSelector):
    """이 클래스는 예약을 DB에서 PULL하는 비즈니스 로직을 담당합니다."""

    def get_queryset_for_ticket_type_uncanceld_reservations(
        self, pet_kindergarden_id: int, reserved_at: str
    ) -> dict[str, list[Reservation]]:
        """반려동물 유치원 아이디와 예약 날짜로 이용권 종류별 취소되지 않은 예약 리스트를 조회합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reserved_at (str): 예약 날짜

        Returns:
            dict: 예약 리스트를 'time', 'all_day', 'hotel' 키로 구분하여 반환하며, 존재하지 않으면 빈 리스트 반환
        """
        time_reservations = []
        all_day_reservations = []
        hotel_reservations = []

        reservations = (
            Reservation.objects.filter(
                pet_kindergarden_id=pet_kindergarden_id,
                reserved_at__date=reserved_at,
            )
            .select_related(
                "customer",
                "customer_pet",
                "customer_ticket",
                "customer_ticket__ticket",
            )
            .filter(
                ~Q(reservation_status=ReservationStatus.CANCELED.value),
                Q(customer_ticket__ticket__ticket_type=TicketType.HOTEL.value, depth=0)
                | ~Q(customer_ticket__ticket__ticket_type=TicketType.HOTEL.value),
            )
        )

        hotel_reservation_ids = []
        for reservation in reservations:
            ticket_type = reservation.customer_ticket.ticket.ticket_type
            if ticket_type == TicketType.TIME.value:
                time_reservations.append(reservation)
            elif ticket_type == TicketType.ALL_DAY.value:
                all_day_reservations.append(reservation)
            elif ticket_type == TicketType.HOTEL.value:
                hotel_reservations.append(reservation)
                hotel_reservation_ids.append(reservation.id)

        if hotel_reservation_ids:
            reservation_tree_end_at = self.get_by_parent_ids_for_end_at(hotel_reservation_ids)
            for reservation in hotel_reservations:
                for end_at_pair in reservation_tree_end_at:
                    if end_at_pair[0] == reservation.id:
                        reservation.end_at = end_at_pair[1]
                        break
        return {"time": time_reservations, "all_day": all_day_reservations, "hotel": hotel_reservations}

    def get_by_id_for_uncanceled_reservation(self, reservation_id: int) -> Optional[Reservation]:
        """예약 아이디로 취소되지 않은 예약을 조회합니다.

        Args:
            reservation_id (int): 예약 아이디

        Returns:
            Optional[Reservation]: 예약이 존재하면 예약 객체를 반환하고, 존재하지 않으면 None을 반환
        """
        try:
            return Reservation.objects.filter(
                Q(id=reservation_id) & ~Q(reservation_status=ReservationStatus.CANCELED.value)
            ).get()

        except Reservation.DoesNotExist:
            return None

    def exists_by_customer_pet_id_and_reserved_at(self, customer_pet_id: int, reserved_at: str) -> bool:
        """고객 반려동물 아이디와 예약 날짜로 예약이 존재하는지 확인합니다.

        Args:
            customer_pet_id (int): 고객 반려동물 아이디
            reserved_at (str): 예약 날짜

        Returns:
            bool: 예약이 존재하면 True를 반환하며, 존재하지 않으면 False를 반환
        """
        return Reservation.objects.filter(customer_pet_id=customer_pet_id, reserved_at__date=reserved_at).exists()

    def get_queryset_with_customer_ticket_and_ticket_by_ids(self, reservation_ids: list[int]) -> QuerySet[Reservation]:
        """예약 아이디 리스트로 고객 티켓과 티켓을 포함한 예약 쿼리셋을 조회합니다.

        Args:
            reservation_ids (list[int]): 예약 아이디 리스트

        Returns:
            QuerySet[Reservation]: 예약 쿼리셋을 반환이며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return Reservation.objects.filter(id__in=reservation_ids).select_related(
            "customer_ticket", "customer_ticket__ticket"
        )

    def get_queryset_by_ids(self, reservation_ids: list[int]) -> QuerySet[Reservation]:
        """예약 아이디 리스트로 예약 쿼리셋을 조회합니다.

        Args:
            reservation_ids (list[int]): 예약 아이디 리스트

        Returns:
            QuerySet[Reservation]: 예약 쿼리셋을 반환하며 존재하지 않으면 빈 쿼리셋을 반환
        """
        return Reservation.objects.filter(id__in=reservation_ids)

    def get_by_parent_ids_for_end_at(self, parent_ids: list[int]) -> list[tuple[int, str]]:
        """부모 예약 아이디로 예약 퇴실 시간을 조회합니다.

        Args:
            parent_ids (list[int]): 부모 예약 아이디 리스트

        Returns:
            list[tuple[int, str]]: 부모 예약 아이디와 예약 퇴실 시간을 튜플로 반환
        """
        with connection.cursor() as cursor:
            query = """
            WITH RECURSIVE CTE AS (
                -- Anchor member
                SELECT parent_id AS root_id, reservation_id, parent_id, depth, end_at AS max_end_at
                FROM reservation
                WHERE parent_id IN %s

                UNION ALL

                -- Recursive member
                SELECT c.root_id, r.reservation_id, r.parent_id, r.depth, r.end_at AS max_end_at
                FROM reservation r
                INNER JOIN CTE c ON r.parent_id = c.reservation_id
            )

            SELECT root_id, max_end_at
            FROM CTE
            WHERE reservation_id NOT IN (SELECT parent_id FROM reservation WHERE parent_id IS NOT NULL);
            """
            cursor.execute(query, [tuple(parent_ids)])
            result = cursor.fetchall()
        return result

    def get_child_ids_by_parent_id(self, parent_id: int) -> list[tuple[int, None]]:
        """부모 예약 아이디로 모든 자식 예약 아이디를 조회합니다.

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

    def get_queryset_for_customer_pet_duplicated_reserved_at(
        self, customer_pet_id: int, reserved_at: str, end_at: str
    ) -> list[Optional[str]]:
        """고객 반려동물 아이디와 예약 시작일과 종료일로 중복된 예약 날짜 리스트를 조회합니다.

        Args:
            customer_pet_id (int): 고객 반려동물 아이디
            reserved_at (str): 예약 시작일
            end_at (str): 예약 종료일

        Returns:
            list[str]: 중복된 예약 날짜 리스트
        """
        duplicated_dates = (
            Reservation.objects.filter(
                customer_pet_id=customer_pet_id, reserved_at__lte=end_at, end_at__gte=reserved_at
            )
            .annotate(reserved_at_str=Cast("reserved_at", DateField()))
            .values_list("reserved_at_str", flat=True)
        )

        return [date.strftime("%Y-%m-%d") for date in duplicated_dates]
