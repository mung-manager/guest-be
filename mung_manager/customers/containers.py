from dependency_injector import containers, providers

from mung_manager.customers.selectors.customer_pets import CustomerPetSelector
from mung_manager.customers.selectors.customer_ticket_registration_logs import (
    CustomerTicketRegistrationLogSelector,
)
from mung_manager.customers.selectors.customer_ticket_usage_logs import (
    CustomerTicketUsageLogSelector,
)
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.customers.selectors.customers import CustomerSelector
from mung_manager.customers.services.customer_tickets import CustomerTicketService
from mung_manager.customers.services.customers import CustomerService
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.tickets.selectors.tickets import TicketSelector


class CustomerContainer(containers.DeclarativeContainer):
    """이 클래스는 DI(Dependency Injection) 고객 컨테이너 입니다.

    Attributes:
        pet_kindergarden_selector: 펫킨더가든 셀렉터
        customer_selector: 고객 셀렉터
        customer_ticket_selector: 고객 티켓 셀렉터
        customer_ticket_usage_log_selector: 고객 티켓 사용 로그 셀렉터
        customer_ticket_registration_log_selector: 고객 티켓 등록 로그 셀렉터
        ticket_selector: 티켓 셀렉터
        reservation_selector: 예약 셀렉터
        customer_ticket_service: 고객 티켓 서비스
        customer_service: 고객 서비스
    """

    pet_kindergarden_selector = providers.Factory(PetKindergardenSelector)
    customer_selector = providers.Factory(CustomerSelector)
    customer_ticket_selector = providers.Factory(CustomerTicketSelector)
    customer_ticket_usage_log_selector = providers.Factory(CustomerTicketUsageLogSelector)
    customer_ticket_registration_log_selector = providers.Factory(CustomerTicketRegistrationLogSelector)
    customer_pet_selector = providers.Factory(CustomerPetSelector)
    ticket_selector = providers.Factory(TicketSelector)
    customer_ticket_service = providers.Factory(
        CustomerTicketService,
        customer_selector=customer_selector,
        pet_kindergarden_selector=pet_kindergarden_selector,
        ticket_selector=ticket_selector,
    )
    customer_service = providers.Factory(
        CustomerService,
        customer_selector=customer_selector,
        customer_pet_selector=customer_pet_selector,
        pet_kindergarden_selector=pet_kindergarden_selector,
    )
