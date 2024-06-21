from dependency_injector import containers, providers

from mung_manager.reservations.selectors.reservations import ReservationSelector
from mung_manager.reservations.services.reservations import ReservationService


class ReservationContainer(containers.DeclarativeContainer):
    """
    이 클래스는 DI(Dependency Injection) 예약 컨테이너 입니다.

    Attributes:
        reservation_selector: 예약 셀렉터
        reservation_service: 예약 서비스
    """

    reservation_selector = providers.Factory(ReservationSelector)
    reservation_service = providers.Factory(ReservationService)
