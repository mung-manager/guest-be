from collections import defaultdict
from typing import Any

from django.utils import timezone

from mung_manager.customers.models import Customer
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.enums import ReservationStatus
from mung_manager.reservations.models import Reservation
from mung_manager.reservations.selectors.abstracts import AbstractReservationSelector
from mung_manager.tickets.enums import TicketType


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
            QuerySet[Reservation]: 예약이 존재하지 않으면 빈 쿼리셋을 반환
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
            if reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value:
                root_reservation = self.find_root(reservation)
                grouped_reservations[root_reservation.id].append(reservation)
            else:
                grouped_reservations[reservation.id].append(reservation)

        # 그룹화된 예약 정보를 딕셔너리로 변환
        for group in grouped_reservations.values():
            if len(group) == 1 and group[0].customer_ticket.ticket.ticket_type != TicketType.HOTEL.value:
                reservation = group[0]
                ticket_type_value = reservation.customer_ticket.ticket.ticket_type
                customer_pet_name = reservation.customer_pet.name
                start_at = reservation.reserved_at
                end_at = reservation.end_at

                ticket_type = (
                    TicketType.TIME.value if ticket_type_value == TicketType.TIME.value else TicketType.ALL_DAY.value
                )
                reservation_list.append(
                    {
                        "ticket_type": ticket_type,
                        "start_at": start_at,
                        "end_at": end_at,
                        "customer_pet_name": customer_pet_name,
                    }
                )
            else:
                ticket_type = TicketType.HOTEL.value
                start_time = min(res.reserved_at for res in group)  # type: ignore
                end_time = max(res.end_at for res in group)  # type: ignore
                customer_pet_name = group[0].customer_pet.name
                reservation_list.append(
                    {
                        "ticket_type": ticket_type,
                        "start_at": start_time,
                        "end_at": end_time,
                        "customer_pet_name": customer_pet_name,
                    }
                )

        return reservation_list
