from django.db import models

from mung_manager.commons.base.models import TimeStampedModel
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.tickets.enums import TicketType


class Ticket(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="ticket_id",
        serialize=False,
        db_comment="티켓 아이디",
    )
    usage_time = models.IntegerField(db_comment="사용 가능한 시간")
    usage_count = models.IntegerField(db_comment="사용 가능한 횟수")
    usage_period_in_days_count = models.IntegerField(db_comment="사용 기간(일) 횟수")
    price = models.IntegerField(db_comment="금액")
    ticket_type = models.CharField(
        max_length=32,
        db_comment="티켓 타입",
        choices=[(t.value, t.name) for t in TicketType],
    )
    deleted_at = models.DateTimeField(db_comment="삭제 일시", blank=True, null=True)
    is_deleted = models.BooleanField(db_comment="삭제 여부", default=False)
    pet_kindergarden = models.ForeignKey(
        PetKindergarden,
        on_delete=models.CASCADE,
        related_name="tickets",
        db_comment="펫 유치원 아이디",
    )

    class Meta:
        db_table = "ticket"
        managed = False
