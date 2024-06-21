from concurrency.fields import IntegerVersionField
from django.db import models

from mung_manager.authentications.models import User
from mung_manager.commons.base.models import TimeStampedModel
from mung_manager.pet_kindergardens.models import PetKindergarden
from mung_manager.reservations.models import Reservation
from mung_manager.tickets.models import Ticket


class Customer(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="customer_id",
        serialize=False,
        db_comment="고객 아이디",
    )
    name = models.CharField(max_length=32, db_comment="고객 이름")
    phone_number = models.CharField(max_length=16, db_comment="전화번호")
    memo = models.TextField(db_comment="메모", blank=True)
    is_active = models.BooleanField(db_comment="활성 여부", default=True)
    pet_kindergarden = models.ForeignKey(
        PetKindergarden,
        on_delete=models.CASCADE,
        related_name="customers",
        db_comment="펫 유치원 아이디",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="customers",
        db_comment="유저 아이디",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "customer"
        managed = False


class CustomerPet(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="customer_pet_id",
        serialize=False,
        db_comment="고객 펫 아이디",
    )
    name = models.CharField(max_length=32, db_comment="반려동물 이름")
    is_deleted = models.BooleanField(db_comment="삭제 여부", default=False)
    deleted_at = models.DateTimeField(db_comment="삭제 시간", blank=True, null=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="customer_pets",
        db_comment="고객 아이디",
    )

    class Meta:
        db_table = "customer_pet"
        managed = False


class CustomerTicket(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="customer_ticket_id",
        serialize=False,
        db_comment="고객 티켓 아이디",
    )
    expired_at = models.DateTimeField(db_comment="만료 시간")
    total_count = models.IntegerField(db_comment="총 횟수")
    used_count = models.IntegerField(db_comment="사용한 횟수")
    unused_count = models.IntegerField(db_comment="잔여 횟수")
    version = IntegerVersionField(db_comment="버전")
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="customer_tickets",
        db_comment="티켓 아이디",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="customer_tickets",
        db_comment="고객 아이디",
    )

    class Meta:
        db_table = "customer_ticket"
        managed = False


class CustomerTicketUsageLog(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="customer_ticket_usage_log_id",
        serialize=False,
        db_comment="고객 티켓 사용 로그 아이디",
    )
    used_count = models.IntegerField(db_comment="사용한 횟수")
    customer_ticket = models.ForeignKey(
        CustomerTicket,
        on_delete=models.CASCADE,
        related_name="customer_ticket_usage_logs",
        db_comment="고객 티켓 아이디",
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="customer_ticket_usage_logs",
        db_comment="예약 아이디",
    )

    class Meta:
        db_table = "customer_ticket_usage_log"
        managed = False


class CustomerTicketRegistrationLog(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="customer_ticket_registration_log_id",
        serialize=False,
        db_comment="고객 티켓 등록 로그 아이디",
    )
    customer_ticket = models.ForeignKey(
        CustomerTicket,
        on_delete=models.CASCADE,
        related_name="customer_ticket_logs",
        db_comment="고객 티켓 아이디",
    )

    class Meta:
        db_table = "customer_ticket_registration_log"
        managed = False
