from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger

from mung_manager_commons.request_manager import NaverCloudAlimtalkManager
from mung_manager_db.models import Customer, PetKindergarden

logger = get_task_logger(__name__)


def format_datetime(dt_string: str) -> str:
    dt = datetime.fromisoformat(dt_string)
    return dt.strftime("%Y년 %m월 %d일 %H시")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_alimtalk_on_ticket_low(
        self,
        reservation_info: dict,
        pet_kindergarden: PetKindergarden,
        customer: Customer,
) -> None:
    """
    이 메서드는 잔여 이용권 개수가 0개 혹은 1개일 때 알림톡을 전송합니다.

    Args:
        reservation_info (dict): 예약 관련 데이터
        pet_kindergarden (PetKindergarden): 반려동물 유치원 데이터
        customer (Customer): 고객 데이터
    """

    def _set_content(template: dict, replacements: dict) -> str:
        """
        이 메서드는 템플릿 내용에서 필요한 필드를 동적으로 치환하여 content를 반환합니다.
        """

        content = template["content"]
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        return content

    def _prepare_message(reservation_info: dict, pet_kindergarden: PetKindergarden, customer: Customer) -> dict:
        """
        이 메서드는 잔여 이용권 개수가 0개 혹은 1개일 때, 각 상황에 맞는 메세지를 생성합니다.
        """

        template_code_map = {
            0: "alertWhenNoTicketsLeft",
            1: "alertWhenOneTicketLeft"
        }
        template_code = template_code_map[reservation_info["remain_count"]]
        response = naver_cloud_alimtalk_manager.get_alimtalk_template(template_code=template_code)
        template = response["camel_case_json"][0]

        if reservation_info["remain_count"] == 0:
            replacements = {
                "#{보호자이름}": customer.name,
                "#{유치원명}": pet_kindergarden.name,
                "#{공개된 유치원 연락처}": pet_kindergarden.phone_number,
            }
        elif reservation_info["remain_count"] == 1:
            replacements = {
                "#{보호자이름}": customer.name,
                "#{유치원명}": pet_kindergarden.name,
                "#{이용권명}": reservation_info["ticket_type"],
                "#{잔여횟수}": reservation_info["remain_count"],
                "#{이용권 사용기한}": format_datetime(reservation_info["ticket_expired_at"]),
                "#{당일 예약 가능 여부}": pet_kindergarden.reservation_availability_option,
            }

        content = _set_content(template, replacements)

        return {
            "template_code": template["templateCode"],
            "plus_friend_id": template["channelId"],
            "content": content,
            "title": template["title"],
            "buttons": template["buttons"]
        }

    try:
        naver_cloud_alimtalk_manager = NaverCloudAlimtalkManager()

        message_info = _prepare_message(
            reservation_info=reservation_info,
            pet_kindergarden=pet_kindergarden,
            customer=customer,
        )

        naver_cloud_alimtalk_manager.send_alimtalk(
            template_code=message_info["template_code"],
            plus_friend_id=message_info["plus_friend_id"],
            to=customer.user.phone_number.replace("-", ""),  # type: ignore
            message={
                "title": message_info["title"],
                "content": message_info["content"],
                "buttons": message_info["buttons"],
            },
        )
    except Exception as exc:
        logger.error(f"Failed to send Alimtalk message: {exc}")
        raise self.retry(exc=exc)
