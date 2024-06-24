from abc import ABC, abstractmethod

from mung_manager.errors.exceptions import NotImplementedException


class AbstractPetKindergardenService(ABC):

    @abstractmethod
    def validate_pet_kindergarden(
            self,
            user,
            pet_kindergarden_id: int
    ) -> None:
        raise NotImplementedException()

