from drf_spectacular.utils import OpenApiExample

ResponseNoContentSchema = OpenApiExample(
    name="204(no_content)",
    summary="[No Content]",
    description="""
    요청이 성공적으로 처리되었지만, 반환할 데이터가 없을 때 반환되는 응답입니다.
    """,
    value=None,
    status_codes=["204"],
    response_only=True,
)
