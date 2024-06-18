from abc import ABC, abstractmethod
from typing import Optional

from django.db.models.query import QuerySet

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.reservations.models import (
    DailyReservation,
    DayOff,
    KoreaSpecialDay,
    Reservation,
)


class AbstractReservationSelector(ABC):
    @abstractmethod
    def get_queryset_for_ticket_type_uncanceld_reservations(
        self, pet_kindergarden_id: int, reserved_at: str
    ) -> dict[str, list[Reservation]]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_id_for_uncanceled_reservation(self, reservation_id: int) -> Optional[Reservation]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_customer_pet_id_and_reserved_at(self, customer_pet_id: int, reserved_at: str) -> bool:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_with_customer_ticket_and_ticket_by_ids(self, reservation_ids: list[int]) -> QuerySet[Reservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_ids(self, reservation_ids: list[int]) -> QuerySet[Reservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_parent_ids_for_end_at(self, parent_ids: list[int]) -> list[tuple[int, str]]:
        raise NotImplementedException()

    @abstractmethod
    def get_child_ids_by_parent_id(self, parent_id: int) -> list[tuple[int, None]]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_for_customer_pet_duplicated_reserved_at(
        self, customer_pet_id: int, reserved_at: str, end_at: str
    ) -> list[Optional[str]]:
        raise NotImplementedException()


class AbstractDailyReservationSelector(ABC):
    @abstractmethod
    def get_queryset_by_year_and_month_and_pet_kindergarden_id(
        self, year: int, month: int, pet_kindergarden_id: int
    ) -> QuerySet[DailyReservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_pet_kindergarden_id_and_reserved_at(
        self, pet_kindergarden_id: int, reserved_at: str
    ) -> QuerySet[DailyReservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
        self, pet_kindergarden_id: int, reserved_at: str, end_at: str
    ) -> QuerySet[DailyReservation]:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_for_overregistered(
        self, pet_kindergarden_id: int, reserved_at: list[str], daily_pet_limit: int
    ) -> list[Optional[str]]:
        raise NotImplementedException()


class AbstractDayOffSelector(ABC):
    @abstractmethod
    def get_queryset_by_pet_kindergarden_id_and_day_off_at(
        self, pet_kindergarden_id: int, year: int, month: int
    ) -> QuerySet[DayOff]:
        raise NotImplementedException()

    @abstractmethod
    def get_by_id(self, day_off_id: int) -> Optional[DayOff]:
        raise NotImplementedException()

    @abstractmethod
    def exists_by_day_off_at_and_pet_kindergarden_id(self, day_off_at: str, pet_kindergarden_id: int) -> bool:
        raise NotImplementedException()

    @abstractmethod
    def get_queryset_by_pet_kindergarden_id_and_day_off_at_for_day_offs(
        self, pet_kindergarden_id: int, day_off_at: list[str]
    ) -> list[Optional[str]]:
        raise NotImplementedException()


class AbstractKoreaSpecialDaySelector(ABC):
    @abstractmethod
    def get_queryset_by_year_and_month(self, year: int, month: int) -> QuerySet[KoreaSpecialDay]:
        raise NotImplementedException()
