from celery import shared_task
from celery.utils.log import get_task_logger

from mung_manager.customers.containers import CustomerContainer
from mung_manager_commons.request_manager import NaverCloudAlimtalkManager

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_alimtalk_on_five_day_left(self) -> None:
    """
    이 테스크는 만료일이 5일 남은 이용권을 대상으로 알림톡을 전송합니다.
    """

    def _set_content(
        template: dict,
        pet_kindergarden_name: str,
        customer_name: str,
        phone_number: str,
        ticket_type: str,
        remain_count: int,
        expired_at: str,
        reservation_availability_option: str,
    ) -> str:
        content = template["content"]
        content = content.replace("#{유치원명}", pet_kindergarden_name)
        content = content.replace("#{보호자이름}", customer_name)
        content = content.replace("#{공개된 유치원 연락처}", phone_number)
        content = content.replace("#{이용권명}", ticket_type)
        content = content.replace("#{잔여횟수}", remain_count)
        content = content.replace("#{이용권 사용기한}", expired_at)
        content = content.replace("#{당일 예약 가능 여부}", reservation_availability_option)
        return content

    try:
        naver_cloud_alimtalk_manager = NaverCloudAlimtalkManager()
        response = naver_cloud_alimtalk_manager.get_alimtalk_template(template_code="alert5DaysToTicketExpiry")
        template = response["camel_case_json"][0]

        customer_ticket_selector = CustomerContainer.customer_ticket_selector()
        customer_tickets = customer_ticket_selector.get_queryset_for_unused_tickets_with_five_days_left()
        if customer_tickets:
            for customer_ticket in customer_tickets:
                visible_phone_number = customer_ticket.customer.pet_kindergarden.visible_phone_number
                user_phone_number = visible_phone_number["user_phone_number"]
                pet_kindergarden_phone_number = visible_phone_number["pet_kindergarden_phone_number"]
                phone_number = f"{user_phone_number}({pet_kindergarden_phone_number})".replace("()", "") \
                    if user_phone_number else pet_kindergarden_phone_number

                reservation_availability_option = (
                    customer_ticket.customer.pet_kindergarden.reservation_availability_option
                )

                content = _set_content(
                    template=template,
                    pet_kindergarden_name=customer_ticket.customer.pet_kindergarden.name,
                    customer_name=customer_ticket.customer.name,
                    phone_number=phone_number,
                    ticket_type=customer_ticket.ticket.ticket_type,
                    remain_count=customer_ticket.unused_count,
                    expired_at=customer_ticket.expired_at.strftime("%Y년 %-m월 %-d일 %-H시"),
                    reservation_availability_option=reservation_availability_option.split()[-1],
                )

                naver_cloud_alimtalk_manager.send_alimtalk(
                    template_code=template["templateCode"],
                    plus_friend_id=template["channelId"],
                    to=customer_ticket.customer.phone_number.replace("-", ""),  # type: ignore
                    message={
                        "title": template["title"],
                        "content": content,
                        "buttons": template["buttons"],
                    },
                )
    except Exception as exc:
        logger.error(f"Failed to send Alimtalk message: {exc}")
        raise self.retry(exc=exc)
