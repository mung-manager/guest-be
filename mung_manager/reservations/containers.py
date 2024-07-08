from dependency_injector import containers, providers

from mung_manager.customers.selectors.customer_ticket_usage_logs import (
    CustomerTicketUsageLogSelector,
)
from mung_manager.reservations.selectors.daily_reservations import (
    DailyReservationSelector,
)
from mung_manager.reservations.selectors.reservations import ReservationSelector
from mung_manager.reservations.services.reservations import ReservationService


class ReservationContainer(containers.DeclarativeContainer):
    """
    이 클래스는 DI(Dependency Injection) 예약 컨테이너 입니다.

    Attributes:
        reservation_selector: 예약 셀렉터
        reservation_service: 예약 서비스
    """

    customer_ticket_usage_log_selector = providers.Factory(CustomerTicketUsageLogSelector)
    daily_reservation_selector = providers.Factory(DailyReservationSelector)
    reservation_selector = providers.Factory(ReservationSelector)
    reservation_service = providers.Factory(
        ReservationService,
        reservation_selector=reservation_selector,
        daily_reservation_selector=daily_reservation_selector,
        customer_ticket_usage_log_selector=customer_ticket_usage_log_selector,
    )
