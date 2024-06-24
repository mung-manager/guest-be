from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import check_object_or_not_found
from mung_manager.pet_kindergardens.services.abstracts import (
    AbstractPetKindergardenService,
)


class PetKindergardenService(AbstractPetKindergardenService):
    """
    이 클래스는 반려동물 유치원를 DB에 PUSH하는 비즈니스 로직을 담당합니다.
    """

    def __init__(self, customer_selector):
        self._customer_selector = customer_selector

    def validate_pet_kindergarten(self, user, pet_kindergarden_id: int) -> None:
        check_object_or_not_found(
            self._customer_selector.exists_by_user_and_pet_kindergarden(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )
