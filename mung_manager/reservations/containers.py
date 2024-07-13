from dependency_injector import containers, providers

from mung_manager.customers.selectors.customer_ticket_usage_logs import (
    CustomerTicketUsageLogSelector,
)
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.reservations.selectors.daily_reservations import (
    DailyReservationSelector,
)
from mung_manager.reservations.selectors.days_off import DayOffSelector
from mung_manager.reservations.selectors.reservations import ReservationSelector
from mung_manager.reservations.services.reservations import ReservationService


class ReservationContainer(containers.DeclarativeContainer):
    """
    이 클래스는 DI(Dependency Injection) 예약 컨테이너 입니다.

    Attributes:
        customer_ticket_selector: 고객 티켓 셀렉터
        pet_kindergarden_selector: 반려동물 유치원 셀렉터
        customer_ticket_usage_log_selector: 고객 티켓 사용 로그 셀렉터
        daily_reservation_selector: 일별 예약 셀렉터
        reservation_selector: 예약 셀렉터
        reservation_service: 예약 서비스
    """

    customer_ticket_selector = providers.Factory(CustomerTicketSelector)
    day_off_selector = providers.Factory(DayOffSelector)
    pet_kindergarden_selector = providers.Factory(PetKindergardenSelector)
    customer_ticket_usage_log_selector = providers.Factory(CustomerTicketUsageLogSelector)
    daily_reservation_selector = providers.Factory(DailyReservationSelector)
    reservation_selector = providers.Factory(ReservationSelector)
    reservation_service = providers.Factory(
        ReservationService,
        reservation_selector=reservation_selector,
        daily_reservation_selector=daily_reservation_selector,
        customer_ticket_usage_log_selector=customer_ticket_usage_log_selector,
        pet_kindergarden_selector=pet_kindergarden_selector,
        day_off_selector=day_off_selector,
        customer_ticket_selector=customer_ticket_selector,
    )
