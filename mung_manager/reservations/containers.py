from dependency_injector import containers, providers

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
        reservation_selector: 예약 셀렉터
        reservation_service: 예약 서비스
        day_off_selector: 휴무일 셀렉터
        korea_special_day_selector: 한국 특별일 셀렉터
    """

    reservation_selector = providers.Factory(ReservationSelector)
    reservation_service = providers.Factory(ReservationService)
    day_off_selector = providers.Factory(DayOffSelector)
    daily_reservation_selector = providers.Factory(DailyReservationSelector)
