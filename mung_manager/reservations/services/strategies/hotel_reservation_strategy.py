from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.customers.models import Customer
from mung_manager.customers.selectors.abstracts import (
    AbstractCustomerPetSelector,
    AbstractCustomerTicketSelector,
)
from mung_manager.errors.exceptions import ValidationException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import (
    AbstractReservationStrategy,
)


class HotelReservationStrategy(AbstractReservationStrategy):

    def __init__(
        self,
        customer_pet_selector: AbstractCustomerPetSelector,
        reservation_service: AbstractReservationService,
        customer_ticket_selector: AbstractCustomerTicketSelector,
    ):

        super().__init__(customer_pet_selector, reservation_service)
        self._customer_ticket_selector = customer_ticket_selector

    def specific_validation(
        self, customer: Customer, pet_kindergarden: PetKindergarden, reservation_data: dict
    ) -> None:

        # 사용 가능한 호텔 타입의 티켓이 존재하는지 검증
        check_object_or_not_found(
            self._customer_ticket_selector.get_queryset_by_customer_for_hotel_ticket_type(customer=customer),
            msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
            code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
        )

        # 하원 날짜가 예약할 수 있는 날짜인지 검증
        if reservation_data["end_date"].strftime(
            "%Y-%m-%d"
        ) not in self._reservation_service.get_available_reservation_dates(
            pet_kindergarden_id=pet_kindergarden.id,
            customer=customer,
            ticket_type=reservation_data["ticket_type"],
            ticket_id=reservation_data.get("ticket_id"),
        ):
            raise ValidationException(
                detail=SYSTEM_CODE.message("INVALID_END_AT"),
                code=SYSTEM_CODE.code("INVALID_END_AT"),
            )

        if not reservation_data["reserved_date"] < reservation_data["end_date"]:
            raise ValidationException(
                detail=SYSTEM_CODE.message("INVALID_END_AT"),
                code=SYSTEM_CODE.code("INVALID_END_AT"),
            )

    # def reserve(self, customer, ticket_id) -> None:
    #     pass
