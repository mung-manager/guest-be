from dependency_injector import containers, providers

from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.tickets.selectors.tickets import TicketSelector
from mung_manager.tickets.services.tickets import TicketService


class TicketContainer(containers.DeclarativeContainer):
    """이 클래스는 DI(Dependency Injection) 티켓 컨테이너 입니다.

    Attributes:
        ticket_selector: 티켓 셀렉터
        pet_kindergarden_selector: 펫 킨더가든 셀렉터
        ticket_service: 티켓 서비스
    """

    ticket_selector = providers.Factory(TicketSelector)
    pet_kindergarden_selector = providers.Factory(PetKindergardenSelector)
    ticket_service = providers.Factory(
        TicketService,
        ticket_selector=ticket_selector,
        pet_kindergarden_selector=pet_kindergarden_selector,
    )
