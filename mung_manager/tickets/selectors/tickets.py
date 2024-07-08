from django.db.models import QuerySet

from mung_manager.tickets.models import Ticket
from mung_manager.tickets.selectors.abstracts import AbstractTicketSelector


class TicketSelector(AbstractTicketSelector):
    """
    이 클래스는 티켓을 DB에서 PULL하는 비즈니스 로직을 담당합니다.
    """

    def get_querset_by_pet_kindergarden_id_for_undeleted_ticket(self, pet_kindergarden_id: int) -> QuerySet[Ticket]:
        """
        이 함수는 반려동물 유치원 아이디로 삭제되지 않은 티켓 쿼리셋을 조회합니다.

        Args:
            pet_kindergarden_id: 반려동물 유치원 아이디입니다.

        Returns:
            QuerySet[Ticket]: 삭제되지 않은 티켓 쿼리셋입니다. 없을 경우 빈 쿼리셋을 반환합니다.
        """
        return Ticket.objects.filter(
            pet_kindergarden_id=pet_kindergarden_id,
            is_deleted=False,
            deleted_at__isnull=True,
        )
