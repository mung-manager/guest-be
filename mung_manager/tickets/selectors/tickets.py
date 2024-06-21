from mung_manager.tickets.selectors.abstracts import AbstractTicketSelector


class TicketSelector(AbstractTicketSelector):
    """
    이 클래스는 티켓을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """
