import datetime as dt
from datetime import timedelta

from concurrency.exceptions import RecordModifiedError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from mung_manager.commons.constants import SYSTEM_CODE
from mung_manager.commons.selectors import (
    check_object_or_not_found,
    get_object_or_not_found,
)
from mung_manager.customers.models import CustomerTicketUsageLog
from mung_manager.customers.selectors.customer_ticket_usage_logs import (
    CustomerTicketUsageLogSelector,
)
from mung_manager.customers.selectors.customer_tickets import CustomerTicketSelector
from mung_manager.customers.selectors.customers import CustomerSelector
from mung_manager.errors.exceptions import ValidationException
from mung_manager.pet_kindergardens.selectors.pet_kindergardens import (
    PetKindergardenSelector,
)
from mung_manager.reservations.enums import ReservationStatus
from mung_manager.reservations.models import DailyReservation, Reservation
from mung_manager.reservations.selectors.daily_reservations import (
    DailyReservationSelector,
)
from mung_manager.reservations.selectors.day_offs import DayOffSelector
from mung_manager.reservations.selectors.reservations import ReservationSelector
from mung_manager.reservations.services.abstracts import AbstractReservationService
from mung_manager.tickets.enums import TicketType


class ReservationService(AbstractReservationService):
    """이 클래스는 예약을 DB에 PUSH하는 비즈니스 로직을 담당합니다."""

    def __init__(
        self,
        pet_kindergarden_selector: PetKindergardenSelector,
        customer_selector: CustomerSelector,
        customer_ticket_selector: CustomerTicketSelector,
        customer_ticket_usage_log_selector: CustomerTicketUsageLogSelector,
        daily_reservation_selector: DailyReservationSelector,
        day_off_selector: DayOffSelector,
        reservation_selector: ReservationSelector,
    ):
        self._pet_kindergarden_selector = pet_kindergarden_selector
        self._customer_selector = customer_selector
        self._customer_ticket_selector = customer_ticket_selector
        self._customer_ticket_usage_log_selector = customer_ticket_usage_log_selector
        self._daily_reservation_selector = daily_reservation_selector
        self._day_off_selector = day_off_selector
        self._reservation_selector = reservation_selector

    @transaction.atomic
    def toggle_reservation_is_attended(self, pet_kindergarden_id: int, reservation_id: int, user) -> Reservation:
        """이 함수는 예약의 출석 활성화/비활성화를 변경합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reservation_id (int): 예약 아이디
            user: 유저 객체

        Returns:
            bool: 예약 출석 상태
        """
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )

        reservation = get_object_or_not_found(
            self._reservation_selector.get_by_id_for_uncanceled_reservation(
                reservation_id=reservation_id,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_RESERVATION"),
            code=SYSTEM_CODE.code("NOT_FOUND_RESERVATION"),
        )

        # 호텔 연박 예약의 경우 자식 예약까지 출석 처리
        if (
            reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value
            and reservation.depth == 0
            and reservation.is_extented is True
        ):
            root_id = reservation.id
            child_ids = self._reservation_selector.get_child_ids_by_parent_id(parent_id=root_id)
            reservation_ids = [root_id] + [child_id[0] for child_id in child_ids]
            reservations = self._reservation_selector.get_queryset_by_ids(reservation_ids=reservation_ids)
            reservations.update(is_attended=not reservation.is_attended)
        else:
            reservation.is_attended = not reservation.is_attended
            reservation.save(update_fields=["is_attended"])

        reservation.is_attended = not reservation.is_attended
        return reservation

    @transaction.atomic
    def register_reservation(
        self,
        pet_kindergarden_id: int,
        customer_ticket_ids: list[int],
        customer_id: int,
        customer_pet_id: int,
        reserved_at,
        end_at,
        user,
    ) -> Reservation:
        """이 함수는 예약을 생성합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            customer_ticket_ids (list[int]): 고객 티켓 아이디 리스트
            customer_id (int): 고객 아이디
            customer_pet_id (int): 고객 반려동물 아이디
            reserved_at (str): 예약 시작 시간
            end_at (str): 예약 종료 시간
            user: 유저 객체

        Returns:
            Reservation: 예약 객체
        """
        # 반려동물 유치원 검증
        pet_kindergarden = get_object_or_not_found(
            self._pet_kindergarden_selector.get_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )

        # 고객 및 고객 반려동물 검증 / 연박 공통
        check_object_or_not_found(
            self._customer_selector.get_by_id_and_customer_pet_id_for_undeleted_customer_pets(
                customer_id=customer_id,
                customer_pet_id=customer_pet_id,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER"),
            code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER"),
        )

        # 반려동물 유치원에 대한 하루 정원 검증 / 연박 공통
        overregistered_reserved_at = self._daily_reservation_selector.get_queryset_for_overregistered(
            pet_kindergarden_id=pet_kindergarden_id,
            reserved_at=[reserved_at, end_at],
            daily_pet_limit=pet_kindergarden.daily_pet_limit,
        )
        if len(overregistered_reserved_at) > 0:
            raise ValidationException(
                detail=f"The daily pet limit has been exceeded: {overregistered_reserved_at}",
                code=SYSTEM_CODE.code("OVER_DAILY_PET_LIMIT"),
            )

        # 휴무일에 대한 예약 검증 / 연박 공통
        day_offs = self._day_off_selector.get_queryset_by_pet_kindergarden_id_and_day_off_at_for_day_offs(
            day_off_at=[reserved_at, end_at],
            pet_kindergarden_id=pet_kindergarden_id,
        )
        if len(day_offs) > 0:
            raise ValidationException(
                detail=f"The pet kindergarden is closed on this day: {day_offs}",
                code=SYSTEM_CODE.code("PET_KINDERGARDEN_CLOSED"),
            )

        # 반려동물 동일 시간 예약 검증 / 연박 공통
        duplication_reserved_at = self._reservation_selector.get_queryset_for_customer_pet_duplicated_reserved_at(
            customer_pet_id=customer_pet_id,
            reserved_at=reserved_at,
            end_at=end_at,
        )
        if len(duplication_reserved_at) > 0:
            raise ValidationException(
                detail=f"Reservation already exists for customer pet.: {duplication_reserved_at}",
                code=SYSTEM_CODE.code("ALREADY_EXISTS_RESERVATION_CUSTOMER_PET"),
            )

        # 만약 티켓이 한개일 경우 / 연박 아닐 경우
        if len(customer_ticket_ids) == 1:
            customer_ticket = self._customer_ticket_selector.get_with_ticket_by_id_and_customer_id(
                customer_ticket_id=customer_ticket_ids[0],
                customer_id=customer_id,
            )
            # 티켓 존재 여부 검증
            if customer_ticket is None:
                raise ValidationException(
                    detail=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_TICKET"),
                )

            # 티켓 만료일 검증
            if customer_ticket.expired_at.date() < timezone.now().date():
                raise ValidationException(
                    detail=SYSTEM_CODE.message("EXPIRED_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("EXPIRED_CUSTOMER_TICKET"),
                )

            # 예약 시간 및 퇴실 시간이 만료일 검증
            if (
                customer_ticket.expired_at.date() < end_at.date()
                or customer_ticket.expired_at.date() < reserved_at.date()
            ):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("INVALID_CUSTOMER_TICKET_EXPIRED_AT"),
                    code=SYSTEM_CODE.code("INVALID_CUSTOMER_TICKET_EXPIRED_AT"),
                )

            # 티켓에 대한 시간 검증
            # 종일권인 경우 00:00:00 ~ 23:59:59 검증
            if customer_ticket.ticket.ticket_type == TicketType.ALL_DAY.value:
                if (
                    reserved_at.date() != end_at.date()
                    or reserved_at.strftime("%H:%M:%S") != str(dt.datetime.strptime("00:00:00", "%H:%M:%S").time())
                    or end_at.strftime("%H:%M:%S") != str(dt.datetime.strptime("23:59:59", "%H:%M:%S").time())
                ):
                    raise ValidationException(
                        detail=SYSTEM_CODE.message("INVALID_RESERVATION_TIME_TICKET_TYPE_ALL_DAY"),
                        code=SYSTEM_CODE.code("INVALID_RESERVATION_TIME_TICKET_TYPE_ALL_DAY"),
                    )
            # 시간권인 경우
            if customer_ticket.ticket.ticket_type == TicketType.TIME.value:
                # 사용 시간 일치 검증
                if (end_at - reserved_at) != timedelta(hours=customer_ticket.ticket.usage_time):
                    raise ValidationException(
                        detail=SYSTEM_CODE.message("INVALID_RESERVATION_TIME_TICKET_TYPE_TIME"),
                        code=SYSTEM_CODE.code("INVALID_RESERVATION_TIME_TICKET_TYPE_TIME"),
                    )

                #  반려견 유치원 영업시간 검증
                if pet_kindergarden.business_start_hour.strftime("%H:%M:%S") < reserved_at.strftime(
                    "%H:%M:%S"
                ) or pet_kindergarden.business_start_hour.strftime("%H:%M:%S") > end_at.strftime("%H:%M:%S"):
                    raise ValidationException(
                        detail=SYSTEM_CODE.message("INVALID_PET_KINDERGARDEN_BUSINESS_HOUR"),
                        code=SYSTEM_CODE.code("INVALID_PET_KINDERGARDEN_BUSINESS_HOUR"),
                    )

            # 호텔권인 경우 1일 이내 예약 검증
            if customer_ticket.ticket.ticket_type == TicketType.HOTEL.value:
                if (end_at - reserved_at) < timedelta(days=1):
                    raise ValidationException(
                        detail=SYSTEM_CODE.message("INVALID_RESERVATION_TIME_TICKET_TYPE_HOTEL"),
                        code=SYSTEM_CODE.code("INVALID_RESERVATION_TIME_TICKET_TYPE_HOTEL"),
                    )

            # 티켓 사용 횟수가 남아있는지 검증
            if customer_ticket.unused_count <= 0 or (
                customer_ticket.ticket.ticket_type == TicketType.HOTEL.value
                and customer_ticket.unused_count < (end_at - reserved_at).days
            ):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("NO_CUSTOMER_TICKET_COUNT"),
                    code=SYSTEM_CODE.code("NO_CUSTOMER_TICKET_COUNT"),
                )

            # 티켓 횟수 증감 처리(낙관적 잠금 처리)
            # 재시도 로직 필요 x -> 유저 혼란 방지
            if (
                customer_ticket.ticket.ticket_type == TicketType.TIME.value
                or customer_ticket.ticket.ticket_type == TicketType.ALL_DAY.value
            ):
                ticket_count = 1
            # 호텔권인 경우 이용권은 1일에 1회로 지정
            else:
                ticket_count = timedelta(days=(end_at - reserved_at).days).days

            try:
                customer_ticket.used_count += ticket_count
                customer_ticket.unused_count -= ticket_count
                customer_ticket.save(update_fields=["used_count", "unused_count", "version"])

            except RecordModifiedError:
                raise ValidationException(
                    detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
                )

            # 예약 생성
            reservation = Reservation.objects.create(
                reserved_at=reserved_at,
                end_at=end_at,
                is_attended=False,
                reservation_status=ReservationStatus.COMPLETED.value,
                pet_kindergarden_id=pet_kindergarden_id,
                customer_id=customer_id,
                customer_pet_id=customer_pet_id,
                customer_ticket_id=customer_ticket.id,
            )

            if customer_ticket.ticket.ticket_type != TicketType.HOTEL.value:
                # 일간 예약 생성 및 증가 처리
                daily_reservations = (
                    self._daily_reservation_selector.get_queryset_by_pet_kindergarden_id_and_reserved_at(
                        pet_kindergarden_id=pet_kindergarden_id,
                        reserved_at=reserved_at,
                    )
                )

                if daily_reservations.exists() is False:
                    if customer_ticket.ticket.ticket_type == TicketType.TIME.value:
                        DailyReservation.objects.create(
                            pet_kindergarden_id=pet_kindergarden_id,
                            reserved_at=reserved_at,
                            total_pet_count=1,
                            time_pet_count=1,
                        )
                    elif customer_ticket.ticket.ticket_type == TicketType.ALL_DAY.value:
                        DailyReservation.objects.create(
                            pet_kindergarden_id=pet_kindergarden_id,
                            reserved_at=reserved_at,
                            total_pet_count=1,
                            all_day_pet_count=1,
                        )
                else:
                    if customer_ticket.ticket.ticket_type == TicketType.TIME.value:
                        daily_reservations.update(
                            time_pet_count=F("time_pet_count") + 1, total_pet_count=F("total_pet_count") + 1
                        )
                    elif customer_ticket.ticket.ticket_type == TicketType.ALL_DAY.value:
                        daily_reservations.update(
                            all_day_pet_count=F("all_day_pet_count") + 1, total_pet_count=F("total_pet_count") + 1
                        )

            else:
                # 일간 예약 생성 및 증가 처리 (호텔권)
                date_range = [(reserved_at + timedelta(days=x)).date() for x in range((end_at - reserved_at).days + 1)]
                existing_daily_reservations = (
                    self._daily_reservation_selector.get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
                        pet_kindergarden_id=pet_kindergarden_id,
                        reserved_at=reserved_at,
                        end_at=end_at,
                    )
                )

                existing_dates = [daily_reservation.reserved_at for daily_reservation in existing_daily_reservations]
                missing_dates = [date for date in date_range if date not in existing_dates]
                existing_daily_reservations.update(
                    hotel_pet_count=F("hotel_pet_count") + 1, total_pet_count=F("total_pet_count") + 1
                )

                DailyReservation.objects.bulk_create(
                    [
                        DailyReservation(
                            pet_kindergarden_id=pet_kindergarden_id,
                            reserved_at=date,
                            total_pet_count=1,
                            hotel_pet_count=1,
                        )
                        for date in missing_dates
                    ]
                )

            # 티켓 사용 내역 생성
            CustomerTicketUsageLog.objects.create(
                customer_ticket_id=customer_ticket.id,
                reservation_id=reservation.id,
                used_count=ticket_count,
            )

            # 연박 예약에 대한 검증 / 호텔권만 가능
        else:
            # 호텔권인 경우 1일 이내 예약 검증
            if (end_at - reserved_at) < timedelta(days=1):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("INVALID_RESERVATION_TIME_TICKET_TYPE_HOTEL"),
                    code=SYSTEM_CODE.code("INVALID_RESERVATION_TIME_TICKET_TYPE_HOTEL"),
                )

            # 티켓 존재 여부 검증
            customer_tickets = self._customer_ticket_selector.get_queryset_for_hotel(
                customer_ticket_ids=customer_ticket_ids,
                customer_id=customer_id,
            )

            # 티켓 존재 여부 검증
            if len(customer_tickets) != len(customer_ticket_ids):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("NOT_FOUND_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("NOT_FOUND_CUSTOMER_TICKET"),
                )

            # 티켓 만료일 검증
            if any(customer_ticket.expired_at.date() < timezone.now().date() for customer_ticket in customer_tickets):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("EXPIRED_CUSTOMER_TICKET"),
                    code=SYSTEM_CODE.code("EXPIRED_CUSTOMER_TICKET"),
                )

            # 티켓 사용 횟수가 남아있는지 검증 customer_ticket 하나라도 사용횟수가 0이면 예외 발생
            if (
                any(customer_ticket.unused_count <= 0 for customer_ticket in customer_tickets)
                or sum(customer_ticket.unused_count for customer_ticket in customer_tickets)
                < (end_at - reserved_at).days
            ):
                raise ValidationException(
                    detail=SYSTEM_CODE.message("NO_CUSTOMER_TICKET_COUNT"),
                    code=SYSTEM_CODE.code("NO_CUSTOMER_TICKET_COUNT"),
                )

            depth = 0
            parent_id = None
            total_ticket_count = timedelta(days=(end_at - reserved_at).days).days
            current_ticket_count = 0
            current_reserved_at = reserved_at

            # 티켓 사용 횟수와 reserved_at, end_at 일치 여부 검증
            for customer_ticket in customer_tickets:
                current_ticket_count = customer_ticket.unused_count
                if total_ticket_count > current_ticket_count:
                    current_end_at = current_reserved_at + timedelta(days=customer_ticket.unused_count)
                    try:
                        customer_ticket.used_count += current_ticket_count
                        customer_ticket.unused_count -= current_ticket_count
                        customer_ticket.save(update_fields=["used_count", "unused_count", "version"])
                    except RecordModifiedError:
                        raise ValidationException(
                            detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                            code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
                        )

                else:
                    current_reserved_at = current_end_at
                    current_end_at = current_reserved_at + timedelta(days=total_ticket_count)
                    try:
                        current_ticket_count = total_ticket_count
                        customer_ticket.used_count += current_ticket_count
                        customer_ticket.unused_count -= current_ticket_count
                        customer_ticket.save(update_fields=["used_count", "unused_count", "version"])
                    except RecordModifiedError:
                        raise ValidationException(
                            detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                            code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
                        )

                # 예약 생성
                reservation = Reservation.objects.create(
                    reserved_at=current_reserved_at,
                    end_at=current_end_at,
                    is_attended=False,
                    parent_id=parent_id,
                    depth=depth,
                    is_extented=True,
                    reservation_status=ReservationStatus.COMPLETED.value,
                    pet_kindergarden_id=pet_kindergarden_id,
                    customer_id=customer_id,
                    customer_pet_id=customer_pet_id,
                    customer_ticket_id=customer_ticket.id,
                )

                # 티켓 사용 내역 생성
                CustomerTicketUsageLog.objects.create(
                    customer_ticket_id=customer_ticket.id,
                    reservation_id=reservation.id,
                    used_count=current_ticket_count,
                )
                depth += 1
                parent_id = reservation.id
                current_reserved_at = current_end_at
                total_ticket_count -= current_ticket_count

            # 일간 예약 생성 및 증가 처리
            date_range = [(reserved_at + timedelta(days=x)).date() for x in range((end_at - reserved_at).days + 1)]
            existing_daily_reservations = (
                self._daily_reservation_selector.get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
                    pet_kindergarden_id=pet_kindergarden_id,
                    reserved_at=reserved_at,
                    end_at=end_at,
                )
            )

            existing_dates = [daily_reservation.reserved_at for daily_reservation in existing_daily_reservations]
            missing_dates = [date for date in date_range if date not in existing_dates]
            existing_daily_reservations.update(
                hotel_pet_count=F("hotel_pet_count") + 1, total_pet_count=F("total_pet_count") + 1
            )

            DailyReservation.objects.bulk_create(
                [
                    DailyReservation(
                        pet_kindergarden_id=pet_kindergarden_id,
                        reserved_at=date,
                        total_pet_count=1,
                        hotel_pet_count=1,
                    )
                    for date in missing_dates
                ]
            )

        return reservation

    @transaction.atomic
    def cancel_reservation(self, pet_kindergarden_id: int, reservation_id: int, user):
        """이 함수는 예약을 취소합니다.

        Args:
            pet_kindergarden_id (int): 반려동물 유치원 아이디
            reservation_id (int): 예약 아이디
            user: 유저 객체

        Returns:
            Reservation: 예약 객체
        """
        # 유저 반려동물 유치원 검증
        check_object_or_not_found(
            self._pet_kindergarden_selector.exists_by_id_and_user(
                pet_kindergarden_id=pet_kindergarden_id,
                user=user,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_PET_KINDERGARDEN"),
            code=SYSTEM_CODE.code("NOT_FOUND_PET_KINDERGARDEN"),
        )

        # 예약이 존재하는지 검증
        reservation = get_object_or_not_found(
            self._reservation_selector.get_by_id_for_uncanceled_reservation(
                reservation_id=reservation_id,
            ),
            msg=SYSTEM_CODE.message("NOT_FOUND_RESERVATION"),
            code=SYSTEM_CODE.code("NOT_FOUND_RESERVATION"),
        )

        # 호텔 연박 예약의 경우 자식 예약까지 변경 처리
        if (
            reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value
            and reservation.depth == 0
            and reservation.is_extented is True
        ):
            root_id = reservation.id
            child_ids = self._reservation_selector.get_child_ids_by_parent_id(parent_id=root_id)
            reservation_ids = [root_id] + [child_id[0] for child_id in child_ids]
            reservations = self._reservation_selector.get_queryset_with_customer_ticket_and_ticket_by_ids(
                reservation_ids=reservation_ids
            )
            reservations.update(reservation_status=ReservationStatus.CANCELED.value)

            # 티켓 사용 횟수 증가(낙관적 잠금 처리)
            # 단. 티켓의 만료기간이 오늘 기준 과거일 경우 이용권 증가를 하지 않음
            for reservation in reservations:
                # 각각의 예약에 대한 만료일이 다르기에 예약별로 처리
                if reservation.customer_ticket.expired_at.date() >= timezone.now().date():
                    try:
                        customer_ticket = reservation.customer_ticket
                        customer_ticket.used_count -= 1
                        customer_ticket.unused_count += 1
                        customer_ticket.save(update_fields=["used_count", "unused_count", "version"])
                    except RecordModifiedError:
                        raise ValidationException(
                            detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                            code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
                        )

            # 티켓 사용 내역 사용 횟수 처리
            reservation_ids = [reservation.id for reservation in reservations]
            customer_ticket_usage_logs = self._customer_ticket_usage_log_selector.get_queryset_by_reservation_ids(
                reservation_ids=reservation_ids,
            )
            customer_ticket_usage_logs.update(used_count=0)

            # 예약 첫번째 예약 날짜와 예약 마지막 퇴실 날짜
            # 일간 예약에서 해당 예약 감소 처리
            reservations_list: list[Reservation] = [reservation for reservation in reservations]
            reserved_at = reservations_list[0].reserved_at
            end_at = reservations_list[-1].end_at
            # @TODO: Fixed Type
            daily_reservations = self._daily_reservation_selector.get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
                pet_kindergarden_id=pet_kindergarden_id,
                reserved_at=reserved_at,  # type: ignore
                end_at=end_at,  # type: ignore
            )

            if reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value:
                daily_reservations.update(
                    total_pet_count=F("total_pet_count") - 1, hotel_pet_count=F("hotel_pet_count") - 1
                )

            if reservation.customer_ticket.ticket.ticket_type == TicketType.TIME.value:
                daily_reservations.update(
                    total_pet_count=F("total_pet_count") - 1, time_pet_count=F("time_pet_count") - 1
                )

            if reservation.customer_ticket.ticket.ticket_type == TicketType.ALL_DAY.value:
                daily_reservations.update(
                    total_pet_count=F("total_pet_count") - 1, all_day_pet_count=F("all_day_pet_count") - 1
                )

        else:
            reservation.reservation_status = ReservationStatus.CANCELED.value
            reservation.save(update_fields=["reservation_status"])

            # 티켓 사용 횟수 증가(낙관적 잠금 처리)
            # 단. 티켓의 만료기간이 오늘 기준 과거일 경우 이용권 증가를 하지 않음
            if reservation.customer_ticket.expired_at.date() >= timezone.now().date():
                try:
                    customet_ticket = reservation.customet_ticket
                    customet_ticket.used_count -= 1
                    customet_ticket.unused_count += 1
                    customet_ticket.save(update_fields=["used_count", "unused_count", "version"])
                except RecordModifiedError:
                    raise ValidationException(
                        detail=SYSTEM_CODE.message("CONFILCT_CUSTOMER_TICKET"),
                        code=SYSTEM_CODE.code("CONFILCT_CUSTOMER_TICKET"),
                    )

            # 티켓 사용 내역 사용 횟수 처리
            customer_ticket_usage_log = self._customer_ticket_usage_log_selector.get_by_reservation_id(
                reservation_id=reservation_id,
            )
            # @TODO: Fixed Type
            customer_ticket_usage_log.used_count = 0  # type: ignore
            customer_ticket_usage_log.save(update_fields=["used_count"])  # type: ignore

            # 일간 예약에서 해당 예약 감소
            daily_reservations = self._daily_reservation_selector.get_by_pet_kindergarden_id_and_reserved_at_and_end_at(
                pet_kindergarden_id=pet_kindergarden_id,
                reserved_at=reservation.reserved_at,
                end_at=reservation.end_at,
            )
            if reservation.customer_ticket.ticket.ticket_type == TicketType.HOTEL.value:
                daily_reservations.update(
                    total_pet_count=F("total_pet_count") - 1, hotel_pet_count=F("hotel_pet_count") - 1
                )

            if reservation.customer_ticket.ticket.ticket_type == TicketType.TIME.value:
                daily_reservations.update(
                    total_pet_count=F("total_pet_count") - 1, time_pet_count=F("time_pet_count") - 1
                )

            if reservation.customer_ticket.ticket.ticket_type == TicketType.ALL_DAY.value:
                daily_reservations.update(
                    total_pet_count=F("total_pet_count") - 1, all_day_pet_count=F("all_day_pet_count") - 1
                )
