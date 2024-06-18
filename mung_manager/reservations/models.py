from django.db import models

from mung_manager.commons.base.models import TimeStampedModel
from mung_manager.reservations.enums import ReservationStatus


class Reservation(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="reservation_id",
        serialize=False,
        db_comment="예약 아이디",
    )
    is_attended = models.BooleanField(db_comment="출석 여부", null=True)
    reserved_at = models.DateTimeField(db_comment="예약 시간")
    end_at = models.DateTimeField(db_comment="퇴실 시간", null=True)
    reservation_status = models.CharField(
        max_length=8,
        db_comment="예약 상태",
        choices=[(r.value, r.name) for r in ReservationStatus],
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        db_comment="부모 예약 아이디",
        null=True,
    )
    depth = models.PositiveIntegerField(
        db_comment="노드 깊이",
        default=0,
    )
    is_extented = models.BooleanField(db_comment="고객 티켓 연장 여부", default=False)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="reservations",
        db_comment="고객 아이디",
    )
    customer_pet = models.ForeignKey(
        "customers.CustomerPet",
        on_delete=models.CASCADE,
        related_name="reservations",
        db_comment="고객 펫 아이디",
    )
    customer_ticket = models.ForeignKey(
        "customers.CustomerTicket",
        on_delete=models.CASCADE,
        related_name="reservations",
        db_comment="고객 티켓 아이디",
    )
    pet_kindergarden = models.ForeignKey(
        "pet_kindergardens.PetKindergarden",
        on_delete=models.CASCADE,
        related_name="reservations",
        db_comment="펫 유치원 아이디",
    )

    class Meta:
        db_table = "reservation"
        managed = False


class DailyReservation(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="daily_reservation_id",
        serialize=False,
        db_comment="일일 예약 아이디",
    )
    reserved_at = models.DateField(db_comment="예약 날짜")
    total_pet_count = models.SmallIntegerField(db_comment="총 반려동물 수", default=0)
    time_pet_count = models.SmallIntegerField(db_comment="시간권 반려동물 수", default=0)
    all_day_pet_count = models.SmallIntegerField(db_comment="종일권 반려동물 수", default=0)
    hotel_pet_count = models.SmallIntegerField(db_comment="호텔 반려동물 수", default=0)
    pet_kindergarden = models.ForeignKey(
        "pet_kindergardens.PetKindergarden",
        on_delete=models.CASCADE,
        related_name="daily_reservations",
        db_comment="펫 유치원 아이디",
    )

    class Meta:
        db_table = "daily_reservation"
        managed = False


class DayOff(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="day_off_id",
        serialize=False,
        db_comment="휴무 아이디",
    )
    day_off_at = models.DateField(db_comment="휴무 날짜")
    pet_kindergarden = models.ForeignKey(
        "pet_kindergardens.PetKindergarden",
        on_delete=models.CASCADE,
        related_name="day_offs",
        db_comment="펫 유치원 아이디",
    )

    class Meta:
        db_table = "day_off"
        managed = False


class KoreaSpecialDay(TimeStampedModel):
    id = models.AutoField(
        auto_created=True,
        primary_key=True,
        db_column="korea_special_day_id",
        serialize=False,
        db_comment="한국 공휴일 아이디",
    )
    name = models.CharField(max_length=64, db_comment="공휴일 이름")
    special_day_at = models.DateField(db_comment="공휴일 날짜")
    is_holiday = models.BooleanField(db_comment="공휴일 여부", default=True)

    class Meta:
        db_table = "korea_special_day"
        managed = False
