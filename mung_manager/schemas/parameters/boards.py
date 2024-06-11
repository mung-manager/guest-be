from drf_spectacular.openapi import OpenApiParameter

from config.settings.swagger.openapi import ParameterOpenApiExample

ParameterKeywordSchema1 = ParameterOpenApiExample(
    name="테스트1",
    field_name="keyword",
    description="검색 키워드",
    value="테스트1",
    parameter_only=OpenApiParameter.QUERY,
)

ParameterKeywordSchema2 = ParameterOpenApiExample(
    name="테스트2",
    field_name="keyword",
    description="검색 키워드",
    value="테스트2",
    parameter_only=OpenApiParameter.QUERY,
)
