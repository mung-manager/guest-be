import csv
from itertools import islice
from typing import List, Optional

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.utils import timezone

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import (
    check_object_or_already_exist,
    check_object_or_not_found,
    get_object_or_not_found,
)
from mung_manager.commons.services import update_model
from mung_manager.commons.validators import (
    InvalidPhoneNumberValidator,
    UniquePetNameValidator,
)
from mung_manager.customers.models import Customer, CustomerPet
from mung_manager.customers.selectors.customer_pets import CustomerPetSelector
from mung_manager.customers.selectors.customers import CustomerSelector
from mung_manager.customers.services.abstracts import AbstractCustomerService
from mung_manager.errors.exceptions import AlreadyExistsException, ValidationException
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)


class CustomerService(AbstractCustomerService):
    """이 클래스는 고객을 DB에서 PUSH하는 비즈니스 로직을 담당합니다."""

    def __init__(
        self,
        customer_selector: CustomerSelector,
        customer_pet_selector: CustomerPetSelector,
        pet_kindergarden_selector: PetKindergardenSelector,
    ):
        self._customer_selector = customer_selector
        self._customer_pet_selector = customer_pet_selector
        self._pet_kindergarden_selector = pet_kindergarden_selector

    @transaction.atomic
    def create_customer(
        self,
        user,
        pet_kindergarden_id: int,
        name: str,
        phone_number: str,
        pets: List[str],
    ) -> Customer:
        """이 함수는 고객을 검증 후 생성합니다.

        Args:
            user: 유저 객체
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            name (str): 고객 이름
            phone_number (str): 고객 전화번호
            pets (List[str]): 반려동물 이름

        Returns:
            Customer: 고객 객체
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
            self._customer_selector.exists_by_pet_kindergarden_id_and_phone_number(
                pet_kindergarden_id=pet_kindergarden_id,
                phone_number=phone_number,
            ),
            msg=SYSTEM_CODE.message("ALREADY_EXISTS_CUSTOMER"),
            code=SYSTEM_CODE.code("ALREADY_EXISTS_CUSTOMER"),
        )

        customer = Customer.objects.create(
            pet_kindergarden_id=pet_kindergarden_id,
            name=name,
            phone_number=phone_number,
        )

        pet_instances = [CustomerPet(name=pet, customer=customer) for pet in pets]

        CustomerPet.objects.bulk_create(pet_instances)

        return customer

    @transaction.atomic
    def create_customers_by_csv(self, user, pet_kindergarden_id: int, csv_file: InMemoryUploadedFile) -> List[Customer]:
        """
        이 함수는 CSV 파일을 읽어서 고객을 생성합니다.

        Args:
            user: 유저 객체
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            csv_file (File): CSV 파일

        Returns:
            QuerySet[Customer]: 고객 객체
        """
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )

        # CSV 파일을 읽어서 데이터 추출
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.reader(decoded_file)

        customer_instances: List[Customer] = []
        pet_instances: List[CustomerPet] = []

        phone_number_validator = InvalidPhoneNumberValidator()
        unique_pet_name_validator = UniquePetNameValidator()

        # CSV 파일을 읽어서 고객 객체를 생성
        for idx, row in islice(enumerate(reader), 3, None):
            # row 데이터 추출
            name, phone_number, pet_data = map(str.strip, row[:3])

            # 이름, 전화번호, 반려동물 빈 값 검사
            if all(value for value in [name, phone_number, pet_data]):
                # 전화번호 유효성 검사
                phone_number_validator(phone_number)

                # 반려동물 이름 중복 검사
                unique_pet_name_validator(pet_data.split(","))

                # csv 파일에 동일한 전화번호가 존재하는지 검증
                if phone_number in [customer.phone_number for customer in customer_instances]:
                    raise ValidationException(
                        detail=SYSTEM_CODE.message("DUPLICATE_PHONE_NUMBER_CSV_FILE"),
                        code=SYSTEM_CODE.code("DUPLICATE_PHONE_NUMBER_CSV_FILE"),
                    )

                # 고객 인스턴스 생성
                customer = Customer(
                    pet_kindergarden_id=pet_kindergarden_id,
                    name=name,
                    phone_number=phone_number,
                )
                customer_instances.append(customer)

                # 고객 반려동물 인스턴스 생성
                pets = [pet.strip() for pet in pet_data.split(",")]
                pet_instances.extend(CustomerPet(name=pet, customer=customer) for pet in pets)

        # csv 파일 닫기
        csv_file.close()

        # 전화번호로 기존 고객이 존재하는지 검증
        original_customer_phone_number_instances = self._customer_selector.get_queryset_by_pet_kindergarden_id(
            pet_kindergarden_id=pet_kindergarden_id
        ).values_list("phone_number", flat=True)

        for customer_instance in customer_instances:
            if customer_instance.phone_number in original_customer_phone_number_instances:
                raise AlreadyExistsException(
                    detail=SYSTEM_CODE.message("ALREADY_EXISTS_CUSTOMER"),
                    code=SYSTEM_CODE.code("ALREADY_EXISTS_CUSTOMER"),
                )

        # 최종 고객, 고객 반려동물 인스턴스 저장
        customers = Customer.objects.bulk_create(customer_instances)
        CustomerPet.objects.bulk_create(pet_instances)
        return customers

    @transaction.atomic
    def toggle_customer_is_active(self, user, customer_id: int, pet_kindergarden_id: int) -> Customer:
        """
        이 함수는 고객의 활성화/비활성화를 변경합니다.

        Args:
            user: 유저 객체
            customer_id (int): 고객 아이디
            pet_kindergarden_id (int): 반려동물 유치원 아이디

        Returns:
            Customer: 고객 객체
        """
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )

        # 고객이 존재하는지 검증
        customer = get_object_or_not_found(
            self._customer_selector.get_by_id(customer_id=customer_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )

        # 고객 활성화/비활성화
        fields = ["is_active"]
        data = {"is_active": not customer.is_active}
        customer, has_updated = update_model(instance=customer, fields=fields, data=data)

        return customer

    @transaction.atomic
    def update_customer(
        self,
        user,
        pet_kindergarden_id: int,
        customer_id: int,
        name: str,
        phone_number: str,
        pets_to_add: List[str],
        pets_to_delete: List[str],
        memo: str,
    ) -> Optional[Customer]:
        """
        이 함수는 고객 정보를 업데이트합니다.

        Args:
            user: 유저 객체
            customer_id (int): 고객 아이디
            name (str): 고객 이름
            phone_number (str): 고객 전화번호
            pets_to_add (List[str]): 추가할 반려동물 이름
            pets_to_delete (List[str]): 삭제할 반려동물 이름
            memo (str): 고객 메모

        Returns:
            Customer: 고객 객체
        """
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )

        # 고객이 존재하는지 검증
        customer = get_object_or_not_found(
            self._customer_selector.get_by_id(customer_id=customer_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )

        # 고객 정보 업데이트
        fields = ["name", "memo"]
        data = {"name": name, "memo": memo}

        # 유저와 연결되어 있지 않은 경우만 전화번호 업데이트
        if customer.user is None:
            fields.append("phone_number")
            data["phone_number"] = phone_number

        customer, has_updated = update_model(instance=customer, fields=fields, data=data)

        # 고객 반려동물 추가/삭제
        if len(pets_to_add) > 0:
            check_object_or_already_exist(
                self._customer_pet_selector.exists_by_names_and_customer_id_for_undeleted_customer_pet(
                    names=pets_to_add, customer_id=customer_id
                ),
                msg=SYSTEM_CODE.message("ALREADY_EXISTS_CUSTOMER_PET"),
                code=SYSTEM_CODE.code("ALREADY_EXISTS_CUSTOMER_PET"),
            )

            CustomerPet.objects.bulk_create([CustomerPet(name=pet, customer=customer) for pet in pets_to_add])

        if len(pets_to_delete) > 0:
            pets_to_be_deleted = (
                self._customer_pet_selector.get_queryset_by_names_and_customer_id_for_undeleted_customer_pet(
                    names=pets_to_delete, customer_id=customer_id
                )
            )

            if len(pets_to_delete) != len(pets_to_be_deleted):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_PET"),
                    code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_PET"),
                )

            pets_to_be_deleted.update(is_deleted=True, deleted_at=timezone.now())

        customer = self._customer_selector.get_with_undeleted_customer_pet_by_id(customer_id=customer_id)
        return customer

    @transaction.atomic
    def register_customer(
        self,
        user,
        customer_id: int,
    ) -> Customer:
        """
        이 함수는 고객 정보에서 비어있는 user_id 값을 채웁니다.

        Args:
            user: 유저 객체
            customer_id (int): 고객 아이디

        Returns:
            Customer: 고객 객체
        """
        # 고객이 존재하는지 검증
        customer = get_object_or_not_found(
            self._customer_selector.get_by_id(customer_id=customer_id),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )

        # 유저 id 업데이트
        fields = ["user"]
        data = {"user": user}

        customer, has_updated = update_model(instance=customer, fields=fields, data=data)

        return customer
