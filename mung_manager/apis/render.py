from typing import Any, Dict, Mapping, Optional

from djangorestframework_camel_case.settings import api_settings
from djangorestframework_camel_case.util import camelize
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from mung_manager.common.constants import SYSTEM_CODE


class CamelCaseJSONRenderer(JSONRenderer):
    """이 클래스는 JSONRenderer를 상속받아 응답 데이터를 정해진 형식으로 변환 후
    CamelCase로 변환하는 JSON 렌더러입니다.

    Attributes:
        default_code (str): 기본 응답 코드
        default_message (str): 기본 응답 메시지
        json_underscoreize (dict): JSON을 언더스코어로 변환할 때 사용할 옵션
    """

    default_code = SYSTEM_CODE.code("SUCCESS")
    default_message = SYSTEM_CODE.message("SUCCESS")
    json_underscoreize = api_settings.JSON_UNDERSCOREIZE

    def get_is_success(self, status_code: int) -> bool:
        """이 함수는 HTTP 상태 코드가 성공 코드인지 확인합니다.

        Args:
            status_code (int): HTTP 상태 코드

        Returns:
            bool: HTTP 상태 코드가 성공 코드이면 True, 아니면 False를 반환
        """
        return status.is_success(status_code)

    def render(
        self,
        data: Dict[str, Any],
        accepted_media_type: Optional[str] = None,
        renderer_context: Optional[Mapping[str, Any]] = None,
    ) -> bytes:
        """이 함수는 응답 데이터를 정해진 형식으로 변환 후 데이터를 CamelCase로 변환합니다.

        Args:
            data (Dict[str, Any]): 응답 데이터
            accepted_media_type (str): 미디어 타입
            renderer_context (Dict[str, Any]): 렌더러 컨텍스트

        Returns:
            bytes: 렌더링된 데이터
        """

        response_data = renderer_context.get("response") if renderer_context else None
        camelize_data = camelize(data, **self.json_underscoreize)

        if response_data is not None:
            response = {
                "success": self.get_is_success(response_data.status_code),
                "statusCode": response_data.status_code,
                "code": self.default_code,
                "message": self.default_message,
                "data": camelize_data,
            }

            if response_data.exception:
                response.update(
                    {
                        "code": camelize_data.get("code"),
                        "message": camelize_data.get("message"),
                        "data": dict(),
                    }
                )
        return super().render(response, accepted_media_type, renderer_context)

    def get_render_schema(self, schema: dict[str, Any], status_code: int) -> dict[str, Any]:
        """이 함수는 응답 스키마를 정의합니다.

        Args:
            schema (dict[str, Any]): 응답 스키마
            status_code (int): HTTP 상태 코드

        Returns:
            dict[str, Any]: 정의된 응답 스키마
        """

        return {
            "properties": {
                "success": {
                    "type": "boolean",
                    "example": self.get_is_success(status_code),
                    "name": "성공 여부",
                },
                "statusCode": {
                    "type": "integer",
                    "example": status_code,
                    "name": "HTTP 상태 코드",
                },
                "code": {
                    "type": "string",
                    "example": self.default_code,
                    "name": "응답 코드",
                },
                "message": {
                    "type": "string",
                    "example": self.default_message,
                    "name": "응답 메시지",
                },
                "data": schema,
            },
        }
