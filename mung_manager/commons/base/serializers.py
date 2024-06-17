import uuid

from rest_framework import serializers

from mung_manager.errors.exceptions import InvalidParameterFormatException


class BaseSerializer(serializers.Serializer):
    """기본 API 입출력 Serializer 클래스입니다.
    data 필드에는 각 API의 입출력 데이터가 정의됩니다.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" in kwargs and not self.is_valid():
            raise InvalidParameterFormatException(self.errors)

        if hasattr(self.Meta, "ref_name"):
            self.Meta.ref_name = str(uuid.uuid4())

    class Meta:
        ref_name = None
