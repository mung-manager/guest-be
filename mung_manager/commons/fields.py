import datetime

from rest_framework import serializers


class TimeFromDateTimeField(serializers.DateTimeField):
    """이 클래스는 DateTimeField를 상속받아 시간만을 처리하는 필드입니다."""

    def to_representation(self, value):
        if isinstance(value, datetime.datetime):
            return value.time()
        return value

    def to_internal_value(self, data):
        try:
            datetime_value = super().to_internal_value(data)
            return datetime_value.time()
        except ValueError:
            raise serializers.ValidationError("Invalid time format. Use HH:MM:SS.")


class DateFromDateTimeField(serializers.DateTimeField):
    """이 클래스는 DateTimeField를 상속받아 날짜만을 처리하는 필드입니다."""

    def to_representation(self, value):
        if isinstance(value, datetime.datetime):
            return value.date()
        return value

    def to_internal_value(self, data):
        try:
            datetime_value = super().to_internal_value(data)
            return datetime_value.date()
        except ValueError:
            raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD.")
