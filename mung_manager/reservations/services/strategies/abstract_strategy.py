from abc import ABC, abstractmethod
from typing import Any, Optional

from mung_manager.customers.selectors.abstracts import AbstractCustomerPetSelector
from mung_manager.errors.exceptions import NotImplementedException, ValidationException
from mung_manager.reservations.selectors.abstracts import AbstractReservationSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager_commons.constants import SYSTEM_CODE
from mung_manager_commons.selector import check_object_or_not_found
from mung_manager_db.enum_types import TicketType
from mung_manager_db.models import Customer, CustomerTicket, PetKindergarden


class AbstractReservationStrategy(ABC):

    def __init__(
        self,
        customer_pet_selector: AbstractCustomerPetSelector,
        reservation_service: AbstractReservationService,
        reservation_selector: AbstractReservationSelector,
    ):
        self._customer_pet_selector = customer_pet_selector
        self._reservation_service = reservation_service
        self._reservation_selector = reservation_selector

    def validate(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
    ) -> None:
        """
        이 함수는 공통 검증 로직과 티켓 타입별 검증 로직을 실행합니다.

        Args:
            customer (Customer): 영업 시작 시간
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력

        Returns:
            None
        """
        self.common_validation(customer, pet_kindergarden, reservation_data)
        self.specific_validation(customer, pet_kindergarden, reservation_data)

    def common_validation(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
    ) -> None:
        """
        이 함수는 티켓 타입별 공통된 내용을 검증합니다.

        Args:
            customer (Customer): 영업 시작 시간
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력

        Returns:
            None
        """
        # 해당 반려동물이 해당 고객에게 속해있는지 검증
        check_object_or_not_found(
            self._customer_pet_selector.exists_by_customer_and_pet_id(
                customer=customer, pet_id=reservation_data["pet_id"]
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_PET"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_PET"),
        )

        if reservation_data["ticket_type"] != TicketType.HOTEL.value:
            # 해당 날에 이미 예약을 했는지 검증
            if reservation_data["reserved_date"].strftime(
                "%Y-%m-%d"
            ) in self._reservation_selector.get_queryset_for_duplicate_reservation(
                customer_id=customer.id,
                customer_pet_id=reservation_data["pet_id"],
                pet_kindergarden_id=pet_kindergarden.id,
            ):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("ALREADY_EXISTS_RESERVATION"),
                    code=SYSTEM_CODE.code("ALREADY_EXISTS_RESERVATION"),
                )

            # 예약하려는 날이 휴무일이나 정원이 초과하는 날인지 검증
            if reservation_data["reserved_date"].strftime(
                "%Y-%m-%d"
            ) not in self._reservation_service.get_available_reservation_dates(
                pet_kindergarden_id=pet_kindergarden.id,
                customer=customer,
                ticket_type=reservation_data["ticket_type"],
                ticket_id=reservation_data.get("ticket_id"),
            ):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("INVALID_RESERVED_AT"),
                    code=SYSTEM_CODE.code("INVALID_RESERVED_AT"),
                )

    @abstractmethod
    def specific_validation(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
    ) -> None:
        raise NotImplementedException()

    def reserve(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        이 함수는 예약 생성과 관련된 로직을 수행합니다.

        Args:
            customer (Customer): 영업 시작 시간
            pet_kindergarden (PetKindergarden): 반려동물 유치원 객체
            reservation_data (dict[str, Any]): 사용자 입력

        Returns:
            dict[str, Any]: 예약 생성 결과 반환
        """
        customer_tickets = self.get_customer_tickets(customer, reservation_data)
        self.handle_daily_reservations(pet_kindergarden, reservation_data, customer)
        reservations = self.create_reservations(customer, pet_kindergarden, reservation_data, customer_tickets)
        self.handle_tickets_usage(customer_tickets, reservations)
        reservation_info = self.get_reservation_info(reservation_data, customer_tickets)

        return reservation_info

    @abstractmethod
    def get_customer_tickets(
        self,
        customer: Customer,
        reservation_data: dict[str, Any],
    ) -> Any:
        raise NotImplementedException()

    @abstractmethod
    def handle_daily_reservations(
        self,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
        customer: Customer,
    ) -> None:
        raise NotImplementedException()

    @abstractmethod
    def create_reservations(
        self,
        customer: Customer,
        pet_kindergarden: PetKindergarden,
        reservation_data: dict[str, Any],
        customer_tickets: Optional[list[CustomerTicket]] = None,
    ) -> Any:
        raise NotImplementedException()

    @abstractmethod
    def handle_tickets_usage(
        self,
        customer_tickets: Any,
        reservations: Any,
    ) -> None:
        raise NotImplementedException()

    @abstractmethod
    def get_reservation_info(
        self,
        reservation_data: dict[str, Any],
        customer_tickets: Any,
    ) -> dict[str, Any]:
        raise NotImplementedException()
