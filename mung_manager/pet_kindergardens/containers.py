from dependency_injector import containers, providers

from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.pet_kindergardens.services.pet_kindergardens import (
    PetKindergardenService,
)


class PetKindergardenContainer(containers.DeclarativeContainer):
    """
    이 클래스는 DI(Dependency Injection) 반려동물 유치원 컨테이너 입니다.

    Attributes:
        pet_kindergarden_selector: 반려동물 유치원 셀렉터
        pet_kindergarden_service: 반려동물 유치원 서비스

    """

    pet_kindergarden_selector = providers.Factory(PetKindergardenSelector)
    pet_kindergarden_service = providers.Factory(PetKindergardenService)
