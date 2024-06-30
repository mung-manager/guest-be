from rest_framework import serializers

from mung_manager.commons.utils import inline_serializer


class CustomerPetSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="반려동물 아이디")
    name = serializers.CharField(label="반려동물 이름")


class CustomerTicketSerializer(serializers.Serializer):
    time = inline_serializer(
        label="시간권 예약",
        many=True,
        fields={
            "id": serializers.IntegerField(label="고객 티켓 아이디"),
            "expired_at": serializers.DateTimeField(label="만료 시간"),
            "unused_count": serializers.IntegerField(label="잔여 횟수"),
            "usage_time": serializers.IntegerField(label="사용 가능한 시간", source="ticket.usage_time"),
        },
    )
    all_day = inline_serializer(
        label="종일권 예약",
        many=True,
        fields={
            "id": serializers.IntegerField(label="고객 티켓 아이디"),
            "expired_at": serializers.DateTimeField(label="만료 시간"),
            "unused_count": serializers.IntegerField(label="잔여 횟수"),
        },
    )
    hotel = inline_serializer(
        label="호텔권 예약",
        many=True,
        fields={
            "id": serializers.IntegerField(label="고객 티켓 아이디"),
            "expired_at": serializers.DateTimeField(label="만료 시간"),
            "unused_count": serializers.IntegerField(label="잔여 횟수"),
        },
    )
