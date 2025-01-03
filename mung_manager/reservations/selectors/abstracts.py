from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Annotated, Any, Optional

from django.db.models import QuerySet
from django_stubs_ext import ValuesQuerySet

from mung_manager.reservations.types import attendance_type, is_expired_type
from mung_manager_commons.errors import NotImplementedException
from mung_manager_db.models import (
    Customer,
    DailyReservation,
    DayOff,
    PetKindergarden,
    Reservation,
)


class AbstractReservationSelector(ABC):

    @abstractmethod
    def get_queryset_by_customer_and_pet_kindergarden(
        self, customer: Customer, pet_kindergarden: PetKindergarden
    ) -> list[dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_customer_and_pet_kindergarden_for_detail(
        self, customer: Customer, pet_kindergarden: PetKindergarden, ticket_status: str
    ) -> QuerySet[Annotated[Reservation, attendance_type]] | list[dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_id_for_uncanceled_reservation(self, reservation_id: int) -> Optional[Reservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_child_ids_by_parent_id(self, parent_id: int) -> list[tuple[int, None]]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_with_customer_ticket_and_ticket_by_ids(self, reservation_ids: list[int]) -> QuerySet[Reservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_with_customer_ticket_by_ids(
        self, reservation_ids: list[int]
    ) -> QuerySet[Annotated[Reservation, is_expired_type], dict[str, Any]]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_for_duplicate_reservation(
        self,
        customer_id: int,
        customer_pet_id: int,
        pet_kindergarden_id: int,
    ) -> list[str]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_for_hotel_type_reservation(
        self,
        customer_id: int,
        customer_pet_id: int,
        pet_kindergarden_id: int,
    ) -> list[str]:
        raise NotImplementedException()


class AbstractDailyReservationSelector(ABC):
    @abstractmethod
    def get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
        self, pet_kindergarden_id: int, reserved_at: datetime, end_at: datetime | None
    ) -> QuerySet[DailyReservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_for_fully_booked(
        self,
        pet_kindergarden_id: int,
        date_range: list[datetime],
        daily_pet_limit: int,
    ) -> ValuesQuerySet[DailyReservation, date] | None:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_pet_kindergarden_id_and_reserved_at(
        self, pet_kindergarden_id: int, reserved_at: str
    ) -> QuerySet[DailyReservation]:
        raise NotImplementedException()


class AbstractDayOffSelector(ABC):
    @abstractmethod
    def get_queryset_by_pet_kindergarden_id_and_date_range_for_day_off(
        self,
        pet_kindergarden_id: int,
        date_range: list[datetime],
    ) -> ValuesQuerySet[DayOff, date]:
        raise NotImplementedException()
