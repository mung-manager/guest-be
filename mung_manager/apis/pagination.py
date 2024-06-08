from collections import OrderedDict
from typing import Any

from rest_framework.pagination import CursorPagination as _CursorPagination
from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination as _PageNumberPagination
from rest_framework.response import Response


def get_paginated_data(*, pagination_class, serializer_class, queryset, request, view):
    """이 함수는 API 응답에 필요한 페이징된 데이터를 생성합니다.

    Args:
        pagination_class (class): 페이징 클래스입니다.
        serializer_class (class): 시리얼라이저 클래스입니다.
        queryset (QuerySet): 쿼리셋입니다.
        request (Request): Request 객체입니다.
        view (View): View 객체입니다.

    Returns:
        serializer.data: 페이징된 데이터를 담는 시리얼라이저 객체입니다.

    """
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_data(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return serializer.data


class LimitOffsetPagination(_LimitOffsetPagination):
    """이 클래스는 LimitOffsetPagination을 상속받아 기본 페이징 설정을 변경합니다."""

    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "name": "페이지 크기"},
                "offset": {"type": "integer", "name": "페이지 오프셋"},
                "count": {"type": "integer", "name": "전체 데이터 개수"},
                "next": {"type": "string", "name": "다음 페이지의 URL"},
                "previous": {"type": "string", "name": "이전 페이지의 URL"},
                "results": {"type": "array", "items": schema, "description": "검색 결과 리스트"},
            },
        }


class CursorPagination(_CursorPagination):
    """이 클래스는 CursorPagination을 상속받아 기본 페이징 설정을 변경합니다."""

    cursor_query_param = "cursor"
    page_size = 10
    ordering = "-created_at"
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "next": {"type": "string", "name": "다음 페이지의 cursor URL"},
                "previous": {
                    "type": "string",
                    "name": "이전 페이지의 cursor URL",
                },
                "results": {"type": "array", "items": schema, "description": "검색 결과 리스트"},
            },
        }


class PageNumberPagination(_PageNumberPagination):
    """이 클래스는 PageNumberPagination을 상속받아 기본 페이징 설정을 변경합니다."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_data(self, data):
        if not self.page:
            return None
        return OrderedDict(
            [
                ("count", self.page.paginator.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "name": "전체 데이터 개수"},
                "next": {"type": "string", "name": "다음 페이지의 URL"},
                "previous": {"type": "string", "name": "이전 페이지의 URL"},
                "results": {"type": "array", "items": schema, "description": "검색 결과 리스트"},
            },
        }
