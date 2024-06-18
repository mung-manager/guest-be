from dependency_injector import containers, providers

from mung_manager.customers.selectors.customer_pets import CustomerPetSelector
from mung_manager.customers.selectors.customer_ticket_usage_logs import (
    CustomerTicketUsageLogSelector,
)
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.customers.selectors.customers import CustomerSelector
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.reservations.selectors.daily_reservations import (
    DailyReservationSelector,
)
from mung_manager.reservations.selectors.day_offs import DayOffSelector
from mung_manager.reservations.selectors.korea_special_days import (
    KoreaSpecialDaySelector,
)
from mung_manager.reservations.selectors.reservations import ReservationSelector
from mung_manager.reservations.services.day_offs import DayOffService
from mung_manager.reservations.services.reservations import ReservationService


class ReservationContainer(containers.DeclarativeContainer):
    """이 클래스는 DI(Dependency Injection) 예약 컨테이너 입니다.

    Attributes:
        pet_kindergarden_selector: 반려동물 유치원 셀렉터
        customer_selector: 고객 셀렉터
        customer_pet_selector: 고객 반려동물 셀렉터
        customer_ticket_selector: 고객 티켓 셀렉터
        customer_ticket_usage_log_selector: 고객 티켓 사용 로그 셀렉터
        daily_reservation_selector: 일일 예약 셀렉터
        reservation_selector: 예약 셀렉터
        day_off_selector: 휴무일 셀렉터
        korea_special_day_selector: 한국 특별일 셀렉터
        day_off_service: 휴무일 서비스
        reservation_service: 예약 서비스
    """

    pet_kindergarden_selector = providers.Factory(PetKindergardenSelector)
    customer_selector = providers.Factory(CustomerSelector)
    customer_pet_selector = providers.Factory(CustomerPetSelector)
    customer_ticket_selector = providers.Factory(CustomerTicketSelector)
    customer_ticket_usage_log_selector = providers.Factory(CustomerTicketUsageLogSelector)
    daily_reservation_selector = providers.Factory(DailyReservationSelector)
    reservation_selector = providers.Factory(ReservationSelector)
    day_off_selector = providers.Factory(DayOffSelector)
    korea_special_day_selector = providers.Factory(KoreaSpecialDaySelector)
    day_off_service = providers.Factory(
        DayOffService,
        day_off_selector=day_off_selector,
        pet_kindergarden_selector=pet_kindergarden_selector,
    )
    reservation_service = providers.Factory(
        ReservationService,
        customer_selector=customer_selector,
        customer_ticket_selector=customer_ticket_selector,
        customer_ticket_usage_log_selector=customer_ticket_usage_log_selector,
        daily_reservation_selector=daily_reservation_selector,
        day_off_selector=day_off_selector,
        reservation_selector=reservation_selector,
        pet_kindergarden_selector=pet_kindergarden_selector,
    )
