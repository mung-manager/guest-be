from datetime import datetime

import pytz
from celery import shared_task
from celery.utils.log import get_task_logger

from mung_manager_commons.request_manager import NaverCloudAlimtalkManager

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_alimtalk_on_ticket_low(
    self,
    customer_name: str,
    customer_phone_number: str,
    remain_count: int,
    ticket_type: str,
    ticket_expired_at: datetime,
    pet_kindergarden_name: str,
    visible_phone_number: dict[str, str],
    reservation_availability_option: str,
) -> None:
    """
    이 메서드는 잔여 이용권 개수가 0개 혹은 1개일 때 알림톡을 전송합니다.

    Args:
        customer_name (str): 고객 이름
        customer_phone_number (str): 고객 전화번호
        remain_count (int): 잔여 이용권 횟수
        ticket_type (str): 이용권 종류
        ticket_expired_at (datetime): 이용권 만료 시간
        pet_kindergarden_name (str): 유치원 이름
        visible_phone_number (dict[str, str]): 노출하는 연락처
        reservation_availability_option (str): 당일 예약 가능 여부
    """

    def _set_content(template: dict, replacements: dict) -> str:
        """
        이 메서드는 템플릿 내용에서 필요한 필드를 동적으로 치환하여 content를 반환합니다.
        """

        content = template["content"]
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))
        return content

    def _prepare_message() -> dict:
        """
        이 메서드는 잔여 이용권 개수가 0개 혹은 1개일 때, 각 상황에 맞는 메세지를 생성합니다.
        """

        template_code_map = {0: "alertWhenNoTicketsLeft", 1: "alertWhenOneTicketLeft"}
        template_code = template_code_map[remain_count]

        response = naver_cloud_alimtalk_manager.get_alimtalk_template(template_code=template_code)
        template = response["camel_case_json"][0]

        if remain_count == 0:
            user_phone_number = visible_phone_number["user_phone_number"]
            pet_kindergarden_phone_number = visible_phone_number["pet_kindergarden_phone_number"]
            phone_number = (
                f"{user_phone_number}({pet_kindergarden_phone_number})".replace("()", "")
                if user_phone_number
                else pet_kindergarden_phone_number
            )

            replacements = {
                "#{보호자이름}": customer_name,
                "#{유치원명}": pet_kindergarden_name,
                "#{공개된 유치원 연락처}": phone_number,
            }
        elif remain_count == 1:
            seoul_tz = pytz.timezone("Asia/Seoul")
            replacements = {
                "#{보호자이름}": customer_name,
                "#{유치원명}": pet_kindergarden_name,
                "#{이용권명}": ticket_type,
                "#{잔여횟수}": remain_count,  # type: ignore
                "#{이용권 사용기한}": ticket_expired_at.astimezone(seoul_tz).date().strftime("%Y년 %m월 %d일"),
                "#{당일 예약 가능 여부}": reservation_availability_option.split()[-1],
            }

        content = _set_content(template, replacements)

        return {
            "template_code": template["templateCode"],
            "plus_friend_id": template["channelId"],
            "content": content,
            "title": template["title"],
            "buttons": template["buttons"],
        }

    try:
        naver_cloud_alimtalk_manager = NaverCloudAlimtalkManager()

        message_info = _prepare_message()

        naver_cloud_alimtalk_manager.send_alimtalk(
            template_code=message_info["template_code"],
            plus_friend_id=message_info["plus_friend_id"],
            to=customer_phone_number,
            message={
                "title": message_info["title"],
                "content": message_info["content"],
                "buttons": message_info["buttons"],
            },
        )
    except Exception as exc:
        logger.error(f"Failed to send Alimtalk message: {exc}")
        raise self.retry(exc=exc)
