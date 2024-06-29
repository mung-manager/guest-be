from dependency_injector import containers, providers

from mung_manager.customers.selectors.customer_pets import CustomerPetSelector
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.customers.selectors.customers import CustomerSelector
from mung_manager.customers.services.customers import CustomerService


class CustomerContainer(containers.DeclarativeContainer):
    """
    이 클래스는 DI(Dependency Injection) 고객 컨테이너 입니다.

    Attributes:
        customer_selector: 고객 셀렉터
        customer_service: 고객 서비스
    """

    customer_selector = providers.Factory(CustomerSelector)
    customer_service = providers.Factory(
        CustomerService,
        customer_selector=customer_selector,
    )
    customer_pet_selector = providers.Factory(CustomerPetSelector)
    customer_ticket_selector = providers.Factory(CustomerTicketSelector)
