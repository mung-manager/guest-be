from dependency_injector import containers, providers

from mung_manager.customers.selectors.customers import CustomerSelector


class ApiContainer(containers.DeclarativeContainer):
    """
    이 클래스는 DI(Dependency Injection) API 컨테이너 입니다.

    Attributes:
        customer_selector: 고객 셀렉터
    """

    customer_selector = providers.Factory(CustomerSelector)
