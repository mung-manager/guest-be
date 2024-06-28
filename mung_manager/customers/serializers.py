from rest_framework import serializers


class CustomerPetSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="반려동물 아이디")
    name = serializers.CharField(label="반려동물 이름")


class CustomerTicketSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="티켓 아이디")
    full_ticket_type = serializers.CharField(label="티켓 타입")
    unused_count = serializers.IntegerField(label="남은 횟수")
    expired_at = serializers.DateTimeField(label="만료 날짜")


class CustomerTicketOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="티켓 아이디")
    unused_count = serializers.IntegerField(label="남은 횟수")
    expired_at = serializers.DateTimeField(label="만료 날짜")
