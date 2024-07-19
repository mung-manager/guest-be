from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.customers.models import Customer
from mung_manager.customers.selectors.abstracts import AbstractCustomerPetSelector, AbstractCustomerTicketSelector
from mung_manager.errors.exceptions import NotFoundException, ValidationException
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.reservations.services.strategies.abstract_strategy import AbstractReservationStrategy


class TimeReservationStrategy(AbstractReservationStrategy):

    def __init__(
            self,
            customer_pet_selector: AbstractCustomerPetSelector,
            reservation_service: AbstractReservationService,
            customer_ticket_selector: AbstractCustomerTicketSelector,
    ):
        super().__init__(customer_pet_selector, reservation_service)
        self._customer_ticket_selector = customer_ticket_selector

    def specific_validation(
            self,
            customer: Customer,
            pet_kindergarden: PetKindergarden,
            reservation_data: dict
    ) -> None:

        # 해당 고객이 주어진 티켓 타입과 티켓 아이디에 해당하는 티켓을 소유하고 있는지 검증
        check_object_or_not_found(
            self._customer_ticket_selector.get_for_all_day_or_time_ticket_type(
                customer=customer,
                ticket_type=reservation_data["ticket_type"],
                ticket_id=reservation_data["ticket_id"],
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_TICKET"),
            code=SYSTEM_CODE.code("NOT_FOUND_TICKET"),
        )

        # 등원 시간 검증
        if reservation_data["attendance_time"].strftime('%H:%M') \
                not in self._reservation_service.get_available_timeslots(
                business_start_hour=pet_kindergarden.business_start_hour,
                business_end_hour=pet_kindergarden.business_end_hour,
                usage_time=int(reservation_data["ticket_type"][:-2]),
        ):
            raise ValidationException(
                detail=SYSTEM_CODE.message("INVALID_ATTENDANCE_TIME"),
                code=SYSTEM_CODE.code("INVALID_ATTENDANCE_TIME"),
            )

    # def reserve(self, customer, ticket_id) -> None:
    #     pass
