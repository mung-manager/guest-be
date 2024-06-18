from abc import ABC, abstractmethod
from typing import List, Tuple

from mung_manager.errors.exceptions import NotImplementedException
from mung_manager.pet_kindergardens.models import PetKindergarden


class AbstractPetKindergardenService(ABC):
    @abstractmethod
    def _get_coordinates_by_road_address(self, road_address: str) -> Tuple[float, float]:
        raise NotImplementedException()

    @abstractmethod
    def create_pet_kindergarden(
        self,
        user,
        name: str,
        profile_thumbnail_url: str,
        phone_number: str,
        visible_phone_number: List[str],
        business_start_hour: str,
        business_end_hour: str,
        road_address: str,
        abbr_address: str,
        detail_address: str,
        short_address: List[str],
        guide_message: str,
        reservation_availability_option: str,
        reservation_change_option: str,
        daily_pet_limit: int,
        main_thumbnail_url: str,
    ) -> PetKindergarden:
        raise NotImplementedException()

    @abstractmethod
    def update_pet_kindergarden(
        self,
        user,
        pet_kindergarden_id: int,
        name: str,
        profile_thumbnail_url: str,
        phone_number: str,
        visible_phone_number: List[str],
        business_start_hour: str,
        business_end_hour: str,
        road_address: str,
        abbr_address: str,
        detail_address: str,
        short_address: List[str],
        guide_message: str,
        reservation_availability_option: str,
        reservation_change_option: str,
        daily_pet_limit: int,
        main_thumbnail_url: str,
    ) -> PetKindergarden:
        raise NotImplementedException()
