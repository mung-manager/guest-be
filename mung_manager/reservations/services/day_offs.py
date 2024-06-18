import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.forms.models import model_to_dict

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.models import DeletedRecord
from mung_manager.commons.selectors import (
    check_object_or_already_exist,
    check_object_or_not_found,
    get_object_or_not_found,
)
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.reservations.models import DayOff
from mung_manager.reservations.selectors.day_offs import DayOffSelector
from mung_manager.reservations.services.abstracts import AbstractDayOffService


class DayOffService(AbstractDayOffService):
    """이 클래스는 휴무일을 DB에 PUSH하는 비즈니스 로직을 담당합니다."""

    def __init__(
        self,
        pet_kindergarden_selector: PetKindergardenSelector,
        day_off_selector: DayOffSelector,
    ):
        self._pet_kindergarden_selector = pet_kindergarden_selector
        self._day_off_selector = day_off_selector

    @transaction.atomic
    def create_day_off(self, pet_kindergarden_id: int, day_off_at: str, user) -> DayOff:
        """이 함수는 휴무일 데이터를 받아 휴무일을 생성합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            day_off_at (str): 휴무일 날짜
            user: 유저 객체

        Returns:
            DayOff: 휴무일 객체
        """
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )
        check_object_or_already_exist(
            self._day_off_selector.exists_by_day_off_at_and_pet_kindergarden_id(
                day_off_at=day_off_at,
                pet_kindergarden_id=pet_kindergarden_id,
            ),
            msg=SYSTEM_CODE.message("ALREADY_EXISTS_DAY_OFF"),
            code=SYSTEM_CODE.code("ALREADY_EXISTS_DAY_OFF"),
        )
        day_off = DayOff.objects.create(
            pet_kindergarden_id=pet_kindergarden_id,
            day_off_at=day_off_at,
        )
        return day_off

    @transaction.atomic
    def delete_day_off(self, pet_kindergarden_id: int, day_off_id: int, user) -> None:
        """이 함수는 휴무일 데이터를 받아 휴무일을 삭제합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            day_off_id (int): 휴무일 아이디
            user: 유저 객체

        Returns:
            None
        """
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )
        day_off = get_object_or_not_found(
            self._day_off_selector.get_by_id(
                day_off_id=day_off_id,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_DAY_OFF"),
            code=SYSTEM_CODE.code("NOT_FOUND_DAY_OFF"),
        )

        day_off_data = model_to_dict(day_off)
        DeletedRecord.objects.create(
            original_table=DayOff.__name__,
            original_id=day_off.id,
            data=json.dumps(day_off_data, cls=DjangoJSONEncoder),
        )

        day_off.delete()
